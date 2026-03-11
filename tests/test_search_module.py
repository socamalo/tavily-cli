"""
Tests for the search module.
"""

import pytest
from unittest.mock import MagicMock

from local_tavily.search import tavily_search


class TestSearchModule:
    """Test cases for the search module."""

    def test_search_success(self, mock_tavily_client, mock_key_manager, sample_search_response):
        """Test successful search."""
        mock_tavily_client.search.return_value = sample_search_response

        result = tavily_search("Python programming")

        assert result["status"] == "success"
        assert result["query"] == "Python programming"
        assert len(result["results"]) == 2
        mock_tavily_client.search.assert_called_once()

    def test_search_with_all_params(self, mock_tavily_client, mock_key_manager):
        """Test search with all parameters."""
        mock_tavily_client.search.return_value = {"results": []}

        result = tavily_search(
            query="AI news",
            search_depth="advanced",
            max_results=15,
            topic="general",  # Use general topic to test country
            time_range="week",
            start_date="2024-01-01",
            end_date="2024-01-31",
            days=7,
            country="us",
            include_domains=["techcrunch.com"],
            exclude_domains=["spam.com"],
            include_answer=True,
            include_images=True,
            include_image_descriptions=True,
            include_raw_content=True,
            include_favicon=True,
            chunks_per_source=3,
            timeout=120,
        )

        assert result["status"] == "success"
        call_args = mock_tavily_client.search.call_args.kwargs
        assert call_args["query"] == "AI news"
        assert call_args["search_depth"] == "advanced"
        assert call_args["max_results"] == 15
        assert call_args["topic"] == "general"
        assert call_args["time_range"] == "week"
        assert call_args["start_date"] == "2024-01-01"
        assert call_args["end_date"] == "2024-01-31"
        assert call_args["days"] == 7
        assert call_args["country"] == "united states"
        assert call_args["include_domains"] == ["techcrunch.com"]
        assert call_args["exclude_domains"] == ["spam.com"]
        assert call_args["include_answer"] is True
        assert call_args["include_images"] is True
        assert call_args["include_image_descriptions"] is True
        assert call_args["include_raw_content"] is True
        assert call_args["include_favicon"] is True
        assert call_args["chunks_per_source"] == 3
        assert call_args["timeout"] == 120

    def test_search_invalid_max_results(self, mock_tavily_client, mock_key_manager):
        """Test search with invalid max_results."""
        result = tavily_search("test", max_results=25)

        assert result["status"] == "error"
        assert "max_results must be between 0 and 20" in result["message"]

    def test_search_invalid_chunks_per_source(self, mock_tavily_client, mock_key_manager):
        """Test search with invalid chunks_per_source."""
        result = tavily_search("test", chunks_per_source=5)

        assert result["status"] == "error"
        assert "chunks_per_source must be between 1 and 3" in result["message"]

    def test_search_invalid_country(self, mock_tavily_client, mock_key_manager):
        """Test search with invalid country."""
        result = tavily_search("test", country="invalid_country_xyz")

        assert result["status"] == "error"
        assert "Invalid country" in result["message"]

    def test_search_api_error(self, mock_tavily_client, mock_key_manager):
        """Test search with API error."""
        mock_tavily_client.search.side_effect = Exception("API Error")

        result = tavily_search("test")

        assert result["status"] == "error"
        assert "API Error" in result["message"]

    def test_search_country_only_with_general_topic(self, mock_tavily_client, mock_key_manager):
        """Test that country is only applied with topic=general."""
        mock_tavily_client.search.return_value = {"results": []}

        # With topic=news, country should not be passed
        result = tavily_search("news", topic="news", country="us")

        assert result["status"] == "success"
        call_args = mock_tavily_client.search.call_args.kwargs
        assert "country" not in call_args
