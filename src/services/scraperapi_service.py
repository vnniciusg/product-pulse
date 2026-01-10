import asyncio

from httpx import AsyncClient, HTTPStatusError, Limits, RequestError
from loguru import logger
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..core.config import app_config
from ..core.models.amazon_product_details import AmazonProductDetails
from ..core.models.amazon_search_result import AmazonSearchResult, SearchProduct
from ..decorators import with_semaphore, with_timer

_semaphore = asyncio.Semaphore(3)

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


class _RateLimitError(Exception): ...


class ScraperAPIService:
    __slots__ = ("_http_client")

    def __init__(self) -> None:
        self._http_client = _HttpxClient(
            base_url="https://api.scraperapi.com/structured/amazon",
            timeout=30.0,
            max_connections=50,
            max_keepalive_connections=10,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(_RateLimitError),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    @with_timer
    async def search_product_on_amazon(
        self, *, query: str, region: str | None = None
    ) -> AmazonSearchResult:
        async with self._http_client as client:
            try:
                response = await client.get(
                    "/search/v1",
                    params={
                        "api_key": app_config.SCRAPER.KEY.get_secret_value(),
                        "query": query,
                        "country_code": region or app_config.SCRAPER.COUNTRY_CODE,
                    },
                )
                response.raise_for_status()
                data = response.json()
                data["results"] = [item for item in data["results"] if "asin" in item]

                return AmazonSearchResult(**data)

            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(
                        f"Rate limit hit for search query '{query}', retrying..."
                    )
                    raise _RateLimitError(f"Rate limit exceeded: {e.response.text}")

                raise
    
    @with_timer
    async def get_products_details(
        self, search_results: list[SearchProduct]
    ) -> list[AmazonProductDetails]:
        async with self._http_client as client:
            asin_to_url = {result.asin: str(result.url) for result in search_results}
            results = await asyncio.gather(
                *[
                    self._get_product_details(asin=asin, url=url, client=client)
                    for asin, url in asin_to_url.items()
                ],
                return_exceptions=True,
            )

            return [result for result in results if isinstance(result, AmazonProductDetails)]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((_RateLimitError, RequestError)),
        before_sleep=before_sleep_log(logger, "WARNING"),
    )
    @with_timer
    @with_semaphore(semaphore=_semaphore)
    async def _get_product_details(
        self, *, asin: str, url: str, client: AsyncClient
    ) -> AmazonProductDetails | None:
        try:
            response = await client.get(
                "/product/v1",
                params={
                    "api_key": app_config.SCRAPER.KEY.get_secret_value(),
                    "asin": asin,
                },
            )
            response.raise_for_status()
            data = response.json()
            data["url"] = url
            return AmazonProductDetails(**data)

        except HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit hit for ASIN {asin}, retrying...")
                raise _RateLimitError(
                    f"Rate limit exceeded for ASIN {asin}: {e.response.text}"
                )

            logger.error(
                f"HTTP error for ASIN {asin}: {e.response.status_code} - {e.response.text}"
            )
            raise

        except RequestError as e:
            logger.warning(f"Request error for ASIN {asin}, retrying: {str(e)}")
            raise

    async def close(self):
        await self._http_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
