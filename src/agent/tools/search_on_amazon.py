from typing import Any

from langchain.tools import ToolRuntime, tool
from loguru import logger

from ...services.scraperapi_service import ScraperAPIService
from .query_refiner import QueryRefiner


@tool
async def search_on_amazon(
    runtime: ToolRuntime, query: str, top_n_products: int = 5
) -> dict[str, Any]:
    """
    Search for products on Amazon that match a given query and return enriched product data.

    What's happening:
    1. Validates and refines the search query to ensure it's single-topic and Amazon-appropriate.
    2. Opens an asynchronous ScraperAPIService session with limited concurrency.
    3. Searches Amazon for products matching the refined query.
    4. Keeps only the top N products from the search results.
    5. Fetches detailed information for each selected product.
    6. Converts product objects into a chatbot-friendly representation.
    7. Returns a structured response indicating success or failure.

    Query Refinement:
    - Removes price filters (e.g., "under $100")
    - Removes shipping filters (e.g., "with prime")
    - Removes rating filters (e.g., "best rated", "5 stars")
    - Reduces multi-topic queries to single topic (e.g., "laptop and mouse" → "laptop")
    - Strips unnecessary qualifiers (e.g., "budget laptop" → "laptop")

    When to call:
    - When a user asks to find or compare products on Amazon.
    - When product discovery is required based on a natural language query.
    - When up-to-date product listings and details are needed for recommendations.

    Args:
    query : str
        The search query to use on Amazon. Can be a natural language query - it will be
        automatically refined to a focused product name or category. Examples:
        - "wireless headphones" (already good)
        - "laptop under $500" (will be refined to "laptop")
        - "Nintendo Switch with prime shipping" (will be refined to "Nintendo Switch")
    top_n_products : int, optional
        The number of top products to return from the search results (default is 5).

    Returns:
    dict[str, Any]
        On success:
            {
                "status": "success",
                "last_search": list[dict],
                "all_searches": list[list[dict]]
            }
            - "last_search" contains chatbot-friendly product representations.
            - "all_searches" contains all preview searchs

        On error:
            {
                "status": "error",
                "error": str
            }
            - "error" contains a generic failure message.
    """
    try:
        # Validate and refine the query for single-topic, Amazon-appropriate search
        validation_result = QueryRefiner.validate_query(query)

        if not validation_result["is_valid"]:
            logger.warning(
                f"Invalid search query: '{query}'. Reason: {validation_result['reason']}"
            )
            return {
                "status": "error",
                "error": f"Invalid search query: {validation_result['reason']}",
            }

        refined_query = validation_result["refined_query"]

        # Log if query was refined
        if refined_query != query:
            logger.info(
                f"Refined search query from '{query}' to '{refined_query}' "
                f"for better Amazon search results"
            )

        async with ScraperAPIService(max_concurrent_requests=3) as scraper_api:
            products = await scraper_api.search_product_on_amazon(
                query=refined_query, region=runtime.state.get("region")
            )
            products = products.top_n_products_only(n=top_n_products)
            products = await scraper_api.get_products_details(search_results=products)
            if not products:
                return {"status": "success", "message": "Not found any product"}

            products = [product.to_chatbot_view() for product in products]

        products_data = [product.model_dump() for product in products]

        return {
            "status": "success",
            "last_search": products_data,
            "all_searches": products_data,
        }

    except Exception as e:
        logger.error(f"An error happend searching on amazon: {str(e)}")
        return {"status": "error", "error": "An error happend searching on amazon"}
