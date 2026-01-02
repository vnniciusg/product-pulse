from httpx import AsyncClient, Limits

from ..core.config import app_config
from ..core.models.amazon_search_result import AmazonSearchResult


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
    __slots__ = "_http_client"

    def __init__(self) -> None:
        self._http_client = _HttpxClient(
            base_url="https://api.scraperapi.com/structured/amazon",
            timeout=30.0,
            max_connections=50,
            max_keepalive_connections=10,
        )

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

    async def close(self):
        await self._http_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
