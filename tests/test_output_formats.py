"""
Tests for output formatters.
"""

import json
import pytest

from local_tavily.formatters import (
    format_search_table,
    format_search_json,
    format_search_markdown,
    format_extract_table,
    format_extract_json,
    format_extract_markdown,
)


class TestSearchFormatters:
    """Test cases for search formatters."""

    def test_format_search_json(self, sample_search_response):
        """Test JSON formatter for search results."""
        result = format_search_json(sample_search_response)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["query"] == "Python programming"
        assert len(parsed["results"]) == 2

    def test_format_search_markdown(self, sample_search_response):
        """Test markdown formatter for search results."""
        result = format_search_markdown(sample_search_response, "Python programming")

        assert "# Search Results: Python programming" in result
        assert "## Results" in result
        assert "Python.org" in result
        assert "https://python.org" in result
        assert "## AI Answer" in result

    def test_format_search_markdown_no_answer(self):
        """Test markdown formatter without answer."""
        results = {
            "status": "success",
            "query": "Test",
            "results": [{"title": "Test", "url": "https://test.com", "score": 0.9}],
            "response_time": 1.0,
        }

        result = format_search_markdown(results, "Test")

        assert "# Search Results: Test" in result
        assert "## AI Answer" not in result

    def test_format_search_markdown_error(self):
        """Test markdown formatter with error."""
        results = {
            "status": "error",
            "message": "Test error",
        }

        result = format_search_markdown(results, "Test")

        assert "**Error:** Test error" in result


class TestExtractFormatters:
    """Test cases for extract formatters."""

    def test_format_extract_json(self, sample_extract_response):
        """Test JSON formatter for extract results."""
        result = format_extract_json(sample_extract_response)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert len(parsed["results"]) == 1

    def test_format_extract_markdown(self, sample_extract_response):
        """Test markdown formatter for extract results."""
        result = format_extract_markdown(sample_extract_response)

        assert "# Extracted Content" in result
        assert "https://example.com" in result
        assert "Example" in result

    def test_format_extract_markdown_with_failures(self):
        """Test markdown formatter with failed extractions."""
        results = {
            "status": "success",
            "results": [{"url": "https://success.com", "content": "Success"}],
            "failed_results": [{"url": "https://failed.com", "error": "Timeout"}],
            "response_time": 1.0,
        }

        result = format_extract_markdown(results)

        assert "(FAILED)" in result
        assert "Timeout" in result

    def test_format_extract_markdown_error(self):
        """Test markdown formatter with error."""
        results = {
            "status": "error",
            "message": "Extraction failed",
        }

        result = format_extract_markdown(results)

        assert "**Error:** Extraction failed" in result
