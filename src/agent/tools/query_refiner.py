"""
Query refinement utilities for Amazon search.

This module provides functionality to validate and refine search queries
to ensure they are focused, single-topic, and appropriate for Amazon search.
"""

import re
from typing import Any


class QueryRefiner:
    """
    Refines search queries to ensure they are single-topic and Amazon-appropriate.
    """

    # Words/phrases that indicate filtering criteria rather than product type
    # These are sorted by length (longest first) to handle multi-word phrases correctly
    FILTER_KEYWORDS = [
        "free shipping",
        "prime shipping",
        "fast delivery",
        "same day delivery",
        "next day shipping",
        "next day",
        "same day",
        "available now",
        "less than",
        "more than",
        "best seller",
        "bestseller",
        "top rated",
        "highly rated",
        "best rated",
        "in stock",
        "on sale",
        "on deal",
        "available",
        "discount",
        "between",
        "expensive",
        "premium",
        "reviews",
        "under",
        "cheap",
        "stars",
        "prime",
        "deal",
        "best",
        "over",
    ]

    # Keywords that can be removed if they're at the beginning
    PREFIX_FILTERS = [
        "best rated",
        "top rated",
        "highly rated",
        "best seller",
        "bestseller",
        "premium",
        "budget",
        "cheap",
        "expensive",
        "best",
        "5 stars",
        "4 stars",
        "5 star",
        "4 star",
    ]

    # Common separators that indicate multiple topics
    MULTI_TOPIC_SEPARATORS = [
        " and ",
        " or ",
        " plus ",
        ",",
    ]

    @staticmethod
    def refine_query(query: str) -> str:
        """
        Refine a search query to focus on a single product topic.

        This method:
        1. Removes filter-related keywords (price, shipping, ratings)
        2. Extracts the core product name/category
        3. Ensures single-topic focus

        Args:
            query: The raw search query from the agent

        Returns:
            A refined, focused search query suitable for Amazon

        Examples:
            >>> QueryRefiner.refine_query("wireless headphones under $100")
            "wireless headphones"

            >>> QueryRefiner.refine_query("laptop with 16gb ram and ssd")
            "laptop"

            >>> QueryRefiner.refine_query("Nintendo Switch with prime shipping")
            "Nintendo Switch"
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        original_query = query
        query = query.strip()
        query_lower = query.lower()

        # Remove prefix filters (best rated, budget, etc.)
        for prefix in QueryRefiner.PREFIX_FILTERS:
            if query_lower.startswith(prefix + " "):
                # Remove the prefix and the space
                query = query[len(prefix) :].strip()
                query_lower = query.lower()
                break

        # Handle multi-topic queries by taking only the first topic
        for separator in QueryRefiner.MULTI_TOPIC_SEPARATORS:
            if separator in query_lower:
                query = query.split(separator)[0].strip()
                query_lower = query.lower()
                break

        # Handle "with" separator - split if it's followed by common accessories/filters
        if " with " in query_lower:
            parts = query.split(" with ", 1)
            if len(parts) == 2:
                second_part = parts[1].lower()
                # Check if second part looks like an accessory, filter, or spec
                if any(
                    word in second_part
                    for word in [
                        "case",
                        "cover",
                        "charger",
                        "cable",
                        "adapter",
                        "memory",
                        "storage",
                        "ram",
                        "gb",
                        "tb",
                        "shipping",
                        "delivery",
                        "prime",
                        "free",
                        "discount",
                        "rgb",
                    ]
                ):
                    query = parts[0].strip()
                    query_lower = query.lower()

        # Remove filter keywords and everything after them
        for filter_keyword in QueryRefiner.FILTER_KEYWORDS:
            pattern = re.compile(rf"\s+{re.escape(filter_keyword)}\b.*", re.IGNORECASE)
            query = pattern.sub("", query)
            query_lower = query.lower()

        # Clean up whitespace
        query = " ".join(query.split())

        # Basic validation - if refinement made query too short, return original
        if len(query) < 2:
            return original_query.strip()

        return query

    @staticmethod
    def validate_query(query: str) -> dict[str, Any]:
        """
        Validate if a query is appropriate for Amazon search.

        Args:
            query: The search query to validate

        Returns:
            A dictionary with validation results:
            {
                "is_valid": bool,
                "reason": str,
                "refined_query": str
            }

        Examples:
            >>> result = QueryRefiner.validate_query("laptop")
            >>> result["is_valid"]
            True

            >>> result = QueryRefiner.validate_query("")
            >>> result["is_valid"]
            False
        """
        if not query or not isinstance(query, str):
            return {
                "is_valid": False,
                "reason": "Query must be a non-empty string",
                "refined_query": None,
            }

        query = query.strip()

        # Check minimum length
        if len(query) < 2:
            return {
                "is_valid": False,
                "reason": "Query is too short (minimum 2 characters)",
                "refined_query": None,
            }

        # Check maximum length (Amazon typically limits to ~200 chars)
        if len(query) > 200:
            return {
                "is_valid": False,
                "reason": "Query is too long (maximum 200 characters)",
                "refined_query": None,
            }

        # Refine the query
        refined = QueryRefiner.refine_query(query)

        # Check if query contains only special characters
        if not re.search(r"[a-zA-Z0-9]", refined):
            return {
                "is_valid": False,
                "reason": "Query must contain alphanumeric characters",
                "refined_query": None,
            }

        return {"is_valid": True, "reason": "Query is valid", "refined_query": refined}

