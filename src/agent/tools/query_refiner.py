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

    # Words that indicate accessories, filters, or specs when used with "with"
    WITH_SEPARATOR_KEYWORDS = [
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

    # Pre-compiled regex patterns for better performance
    _compiled_filter_patterns = None
    _with_keywords_pattern = None

    @classmethod
    def _get_filter_patterns(cls):
        """Lazily compile and cache filter keyword patterns."""
        if cls._compiled_filter_patterns is None:
            cls._compiled_filter_patterns = [
                re.compile(rf"\s+{re.escape(keyword)}\b.*", re.IGNORECASE)
                for keyword in cls.FILTER_KEYWORDS
            ]
        return cls._compiled_filter_patterns

    @classmethod
    def _get_with_keywords_pattern(cls):
        """Lazily compile and cache pattern for WITH separator keywords."""
        if cls._with_keywords_pattern is None:
            # Create pattern with word boundaries for each keyword
            keywords_pattern = "|".join(
                rf"\b{re.escape(word)}\b" for word in cls.WITH_SEPARATOR_KEYWORDS
            )
            cls._with_keywords_pattern = re.compile(keywords_pattern, re.IGNORECASE)
        return cls._with_keywords_pattern

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

        # Remove prefix filters (best rated, budget, etc.) using word boundaries
        for prefix in QueryRefiner.PREFIX_FILTERS:
            # Use word boundary to ensure we match complete words
            pattern = re.compile(rf"^{re.escape(prefix)}\s+", re.IGNORECASE)
            query = pattern.sub("", query)
            query_lower = query.lower()

        # Handle multi-topic queries by taking only the first topic
        for separator in QueryRefiner.MULTI_TOPIC_SEPARATORS:
            if separator in query_lower:
                query = query.split(separator)[0].strip()
                query_lower = query.lower()
                break

        # Handle "with" separator - split if followed by common accessories/filters
        if " with " in query_lower:
            parts = query.split(" with ", 1)
            if len(parts) == 2:
                second_part = parts[1]
                # Use compiled pattern with word boundaries for matching
                pattern = QueryRefiner._get_with_keywords_pattern()
                if pattern.search(second_part):
                    query = parts[0].strip()
                    query_lower = query.lower()

        # Remove filter keywords and everything after them using pre-compiled patterns
        filter_patterns = QueryRefiner._get_filter_patterns()
        for pattern in filter_patterns:
            query = pattern.sub("", query)

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


