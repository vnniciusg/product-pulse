import asyncio

from httpx import AsyncClient, HTTPStatusError, Limits, RequestError
from loguru import logger

from ..core.config import app_config
from ..core.models.amazon_product_details import AmazonProductDetails
from ..core.models.amazon_search_result import AmazonSearchResult, SearchProduct


class _HttpxClient:
    __slots__ = ("_base_url", "_timeout", "_client", "_limits")

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._client: AsyncClient | None = None

        self._limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )

    def _get_client(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                limits=self._limits,
                http2=True,
            )

        return self._client

    async def __aenter__(self) -> AsyncClient:
        return self._get_client()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> AsyncClient:
        await self.close()

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def is_closed(self) -> bool:
        return self._client is None or self._client.is_closed


class ScraperAPIService:
    __slots__ = ("_http_client", "_semaphore")

    def __init__(self, *, max_concurrent_requests: int = 10) -> None:
        self._http_client = _HttpxClient(
            base_url="https://api.scraperapi.com/structured/amazon",
            timeout=30.0,
            max_connections=50,
            max_keepalive_connections=10,
        )
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def search_product_on_amazon(self, *, query: str) -> AmazonSearchResult:
        async with self._http_client as client:
            response = await client.get(
                "/search/v1",
                params={
                    "api_key": app_config.SCRAPER.KEY.get_secret_value(),
                    "query": query,
                },
            )
            response.raise_for_status()

            return AmazonSearchResult(**response.json())

    async def get_products_details(
        self, search_results: list[SearchProduct]
    ) -> list[AmazonProductDetails]:
        async with self._http_client as client:
            asins = [result.asin for result in search_results]
            results = await asyncio.gather(
                *[
                    self._get_product_details(asin=asin, client=client)
                    for asin in asins
                ],
                return_exceptions=True,
            )

            return [result for result in results if result is not None]

    async def _get_product_details(
        self, *, asin: str, client: AsyncClient
    ) -> AmazonProductDetails | None:
        async with self._semaphore:
            try:
                response = await client.get(
                    "/product/v1",
                    params={
                        "api_key": app_config.SCRAPER.KEY.get_secret_value(),
                        "asin": asin,
                    },
                )
                response.raise_for_status()
                return AmazonProductDetails(**response.json())

            except HTTPStatusError as e:
                logger.error(
                    f"HTTP error for ASIN {asin}: {e.response.status_code} - {e.response.text}"
                )
                return None

            except RequestError as e:
                logger.error(f"Request error for ASIN {asin}: {str(e)}")
                return None

            except Exception as e:
                logger.exception(f"Unexpected error for ASIN {asin}: {str(e)}")
                return None

    async def close(self):
        await self._http_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
