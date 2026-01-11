import asyncio
import json
from typing import Any

from langchain_core.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command
from loguru import logger

from ...services.scraperapi_service import ScraperAPIService
from ...decorators import with_timer, with_semaphore


@tool
@with_timer
@with_semaphore(semaphore=asyncio.Semaphore(2))
async def search_on_amazon(
    runtime: ToolRuntime,
    query: str,
    top_n_products: int = 5,
    min_rating: float | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    prime_only: bool = False,
    best_sellers_only: bool = False,
) -> Command:
    """
    Search for products on Amazon and return enriched product data with optional filters.

    Args:
        query: Short search query (2-5 words). Examples: "gaming mouse", "iPhone 15 case", "wireless headphones".
        top_n_products: Number of top products to return (default 5).
        min_rating: Minimum star rating filter (e.g., 4.0 or 4.5).
        min_price: Minimum price in dollars.
        max_price: Maximum price in dollars.
        prime_only: If True, return only Prime-eligible products.
        best_sellers_only: If True, return only best-seller products.

    Returns:
        dict with status, last_search results, and all_searches history.
    """
    try:
        async with ScraperAPIService() as scraper_api:
            search_result = await scraper_api.search_product_on_amazon(
                query=query, region=runtime.state.get("region")
            )

            products = search_result.results

            if prime_only:
                products = [p for p in products if p.has_prime]

            if best_sellers_only:
                products = [p for p in products if p.is_best_seller]

            if min_rating is not None:
                products = [p for p in products if p.stars and p.stars >= min_rating]

            if min_price is not None or max_price is not None:
                min_p = min_price if min_price is not None else 0
                max_p = max_price if max_price is not None else float("inf")
                products = [
                    p for p in products if p.price and min_p <= p.price <= max_p
                ]

            products = products[:top_n_products]

            if not products:
                return {"status": "success", "message": "No products found matching criteria"}

            product_details = await scraper_api.get_products_details(search_results=products)

            if not product_details:
                return {"status": "success", "message": "No product details available"}

            chatbot_views = [product.to_chatbot_view() for product in product_details]

        products_data = [view.model_dump() for view in chatbot_views]

        return Command(
            update={
                "messages": [ToolMessage(
                    content=json.dumps({
                        "status": "success", 
                        "last_search": products_data,
                        "count": len(products_data)
                    }),
                    tool_call_id=runtime.tool_call_id,
                    status="success"
                )],
                "last_search": products_data,
            }
        )

    except Exception as e:
        logger.error(f"Error searching on Amazon: {str(e)}")
        return {"status": "error", "error": "An error occurred while searching on Amazon"}

