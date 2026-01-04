from typing import Any

from langchain.tools import ToolRuntime, tool
from loguru import logger

from ...services.scraperapi_service import ScraperAPIService


@tool
async def search_on_amazon(
    runtime: ToolRuntime, query: str, top_n_products: int = 5
) -> dict[str, Any]:
    """
    Search for products on Amazon that match a given query and return enriched product data.

    What's happening:
    1. Opens an asynchronous ScraperAPIService session with limited concurrency.
    2. Searches Amazon for products matching the provided query.
    3. Keeps only the top N products from the search results.
    4. Fetches detailed information for each selected product.
    5. Converts product objects into a chatbot-friendly representation.
    6. Returns a structured response indicating success or failure.

    When to call:
    - When a user asks to find or compare products on Amazon.
    - When product discovery is required based on a natural language query.
    - When up-to-date product listings and details are needed for recommendations.

    Args:
    query : str
        The search query to use on Amazon (e.g., product name, category, or keywords).
    top_n_products : int, optional
        The number of top products to return from the search results (default is 5).

    Returns:
    dict[str, Any]
        On success:
            {
                "status": "success",
                "products": list[dict]
            }
            - "products" contains chatbot-friendly product representations.

        On error:
            {
                "status": "error",
                "error": str
            }
            - "error" contains a generic failure message.
    """
    try:
        async with ScraperAPIService(max_concurrent_requests=5) as scraper_api:
            products = await scraper_api.search_product_on_amazon(
                query=query, region=runtime.state.get("region")
            )
            products = products.top_n_products_only(n=top_n_products)
            products = await scraper_api.get_products_details(search_results=products)
            products = [product.to_chatbot_view() for product in products]

        products_data = [product.model_dump() for product in products]

        return {
            "status": "success",
            "products": products_data,
            "last_search": products_data,
            "all_searches": products_data,
        }

    except Exception as e:
        logger.error(f"An error happend searching on amazon: {str(e)}")
        return {"status": "error", "error": "An error happend searching on amazon"}
