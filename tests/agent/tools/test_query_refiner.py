"""
Unit tests for query refinement utilities.

Tests validate that search queries are properly refined to be:
1. Single-topic (one product at a time)
2. Amazon-appropriate (clean, focused product names)
3. Free of unnecessary filters (price, shipping, ratings)
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import the module directly without going through agent package
# This avoids importing langchain dependencies that are not needed for testing
project_root = Path(__file__).parent.parent.parent.parent
query_refiner_path = project_root / "src" / "agent" / "tools" / "query_refiner.py"

# Load the module
spec = importlib.util.spec_from_file_location("query_refiner", query_refiner_path)
query_refiner_module = importlib.util.module_from_spec(spec)
sys.modules["query_refiner"] = query_refiner_module
spec.loader.exec_module(query_refiner_module)

QueryRefiner = query_refiner_module.QueryRefiner


class TestQueryRefiner:
    """Test suite for QueryRefiner class."""

    def test_refine_query_removes_price_filters(self):
        """Test that price-related filters are removed from queries."""
        test_cases = [
            ("wireless headphones under $100", "wireless headphones"),
            ("laptop less than $500", "laptop"),
            ("shoes over $50", "shoes"),
            ("gaming mouse between $30 and $50", "gaming mouse"),
            ("budget smartphone", "smartphone"),
            ("cheap tablet", "tablet"),
            ("premium coffee maker", "coffee maker"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_removes_shipping_filters(self):
        """Test that shipping-related filters are removed from queries."""
        test_cases = [
            ("Nintendo Switch with prime shipping", "Nintendo Switch"),
            ("yoga mat with free shipping", "yoga mat"),
            ("keyboard with fast delivery", "keyboard"),
            ("monitor with same day delivery", "monitor"),
            ("book with next day shipping", "book"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_removes_rating_filters(self):
        """Test that rating-related filters are removed from queries."""
        test_cases = [
            ("best rated headphones", "headphones"),
            ("top rated laptop", "laptop"),
            ("highly rated coffee maker", "coffee maker"),
            ("5 stars microwave", "microwave"),
            ("bestseller book", "book"),
            ("best seller phone case", "phone case"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_removes_availability_filters(self):
        """Test that availability-related filters are removed from queries."""
        test_cases = [
            ("camera in stock", "camera"),
            ("laptop available now", "laptop"),
            ("PS5 in stock", "PS5"),
            ("phone on sale", "phone"),
            ("tablet with discount", "tablet"),
            ("watch on deal", "watch"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_handles_multi_topic_with_and(self):
        """Test that multi-topic queries with 'and' are reduced to single topic."""
        test_cases = [
            ("laptop and mouse", "laptop"),
            ("phone and case", "phone"),
            ("camera and tripod", "camera"),
            ("keyboard and mouse pad", "keyboard"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_handles_multi_topic_with_or(self):
        """Test that multi-topic queries with 'or' are reduced to single topic."""
        test_cases = [
            ("laptop or desktop", "laptop"),
            ("tablet or iPad", "tablet"),
            ("headphones or earbuds", "headphones"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_handles_multi_topic_with_comma(self):
        """Test that multi-topic queries with commas are reduced to single topic."""
        test_cases = [
            ("laptop, mouse, keyboard", "laptop"),
            ("phone, case, charger", "phone"),
            ("camera, lens, bag", "camera"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_handles_with_correctly(self):
        """Test that 'with' is handled correctly - splits for accessories but not product features."""
        # These should split (accessories/addons)
        test_cases_split = [
            ("laptop with case", "laptop"),
            ("phone with charger", "phone"),
            ("camera with memory card", "camera"),
            ("laptop with 16gb ram", "laptop"),
            ("phone with 128gb storage", "phone"),
        ]

        for input_query, expected in test_cases_split:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_preserves_good_queries(self):
        """Test that already good queries are preserved."""
        good_queries = [
            "wireless headphones",
            "Nintendo Switch",
            "yoga mat",
            "coffee maker",
            "laptop",
            "mechanical keyboard",
            "running shoes",
            "desk lamp",
            "iPhone 15",
            "Samsung Galaxy",
        ]

        for query in good_queries:
            result = QueryRefiner.refine_query(query)
            assert result == query, f"Good query was modified: '{query}' -> '{result}'"

    def test_refine_query_handles_whitespace(self):
        """Test that extra whitespace is cleaned up."""
        test_cases = [
            ("  laptop  ", "laptop"),
            ("wireless    headphones", "wireless headphones"),
            ("  gaming   mouse  ", "gaming mouse"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_complex_scenarios(self):
        """Test complex real-world scenarios."""
        test_cases = [
            (
                "wireless noise cancelling headphones under $100 with prime shipping",
                "wireless noise cancelling headphones",
            ),
            (
                "best rated gaming laptop with 16gb ram under $1000",
                "gaming laptop",
            ),
            (
                "mechanical keyboard and gaming mouse with rgb under $150",
                "mechanical keyboard",
            ),
            (
                "Nintendo Switch OLED with prime and fast delivery",
                "Nintendo Switch OLED",
            ),
            ("yoga mat on sale cheap under $20", "yoga mat"),
        ]

        for input_query, expected in test_cases:
            result = QueryRefiner.refine_query(input_query)
            assert result == expected, f"Failed for query: '{input_query}'"

    def test_refine_query_raises_on_invalid_input(self):
        """Test that ValueError is raised for invalid inputs."""
        with pytest.raises(ValueError):
            QueryRefiner.refine_query(None)

        with pytest.raises(ValueError):
            QueryRefiner.refine_query("")

        with pytest.raises(ValueError):
            QueryRefiner.refine_query(123)

    def test_refine_query_handles_edge_cases(self):
        """Test edge cases."""
        # Very short query
        result = QueryRefiner.refine_query("tv")
        assert result == "tv"

        # Query that becomes too short after refinement should return original
        result = QueryRefiner.refine_query("a under $100")
        assert result == "a under $100"

    def test_validate_query_accepts_valid_queries(self):
        """Test that valid queries are accepted."""
        valid_queries = [
            "laptop",
            "wireless headphones",
            "Nintendo Switch",
            "yoga mat",
            "ab",  # minimum 2 chars
        ]

        for query in valid_queries:
            result = QueryRefiner.validate_query(query)
            assert result["is_valid"] is True
            assert result["refined_query"] is not None

    def test_validate_query_rejects_invalid_queries(self):
        """Test that invalid queries are rejected."""
        invalid_cases = [
            ("", "non-empty"),
            ("a", "too short"),
            (None, "non-empty string"),
            (123, "non-empty string"),
            ("x" * 201, "too long"),  # over 200 chars
            ("   ", "too short"),  # spaces get stripped, becoming empty
            ("!!!", "alphanumeric"),
        ]

        for query, reason_keyword in invalid_cases:
            result = QueryRefiner.validate_query(query)
            assert result["is_valid"] is False
            assert reason_keyword in result["reason"].lower()
            assert result["refined_query"] is None

    def test_validate_query_provides_refined_query(self):
        """Test that validate_query returns the refined version."""
        test_cases = [
            ("laptop under $500", "laptop"),
            ("wireless headphones with prime", "wireless headphones"),
            ("keyboard and mouse", "keyboard"),
        ]

        for input_query, expected_refined in test_cases:
            result = QueryRefiner.validate_query(input_query)
            assert result["is_valid"] is True
            assert result["refined_query"] == expected_refined

    def test_validate_query_comprehensive(self):
        """Comprehensive validation test."""
        # Valid query
        result = QueryRefiner.validate_query("gaming laptop")
        assert result["is_valid"] is True
        assert result["reason"] == "Query is valid"
        assert result["refined_query"] == "gaming laptop"

        # Query that needs refinement
        result = QueryRefiner.validate_query("gaming laptop under $1000")
        assert result["is_valid"] is True
        assert result["reason"] == "Query is valid"
        assert result["refined_query"] == "gaming laptop"

        # Invalid query
        result = QueryRefiner.validate_query("")
        assert result["is_valid"] is False
        assert "non-empty" in result["reason"].lower()
        assert result["refined_query"] is None
