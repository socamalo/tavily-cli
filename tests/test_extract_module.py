"""
Tests for the extract module.
"""

import pytest

from local_tavily.extract import tavily_extract


class TestExtractModule:
    """Test cases for the extract module."""

    def test_extract_success(self, mocker, sample_extract_response):
        """Test successful extraction."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        mock_client_class = mocker.patch("local_tavily.extract.TavilyClient")
        mock_client = mocker.MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.extract.return_value = sample_extract_response

        result = tavily_extract("https://example.com")

        assert result["status"] == "success"
        assert len(result["results"]) == 1
        mock_client.extract.assert_called_once()

    def test_extract_multiple_urls(self, mocker):
        """Test extraction with multiple URLs."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        mock_client_class = mocker.patch("local_tavily.extract.TavilyClient")
        mock_client = mocker.MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.extract.return_value = {"results": [], "failed_results": []}

        urls = ["https://site1.com", "https://site2.com"]
        result = tavily_extract(urls)

        assert result["status"] == "success"
        call_args = mock_client.extract.call_args.kwargs
        assert call_args["urls"] == urls

    def test_extract_too_many_urls(self, mocker):
        """Test extraction with too many URLs."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        urls = [f"https://site{i}.com" for i in range(21)]
        result = tavily_extract(urls)

        assert result["status"] == "error"
        assert "Maximum 20 URLs" in result["message"]

    def test_extract_with_all_params(self, mocker):
        """Test extraction with all parameters."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        mock_client_class = mocker.patch("local_tavily.extract.TavilyClient")
        mock_client = mocker.MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.extract.return_value = {"results": [], "failed_results": []}

        result = tavily_extract(
            urls="https://example.com",
            extract_depth="advanced",
            include_images=True,
            format="text",
            timeout=30.0,
            include_favicon=True,
        )

        assert result["status"] == "success"
        call_args = mock_client.extract.call_args.kwargs
        assert call_args["urls"] == ["https://example.com"]
        assert call_args["extract_depth"] == "advanced"
        assert call_args["include_images"] is True
        assert call_args["format"] == "text"
        assert call_args["timeout"] == 30.0
        assert call_args["include_favicon"] is True

    def test_extract_api_error(self, mocker):
        """Test extraction with API error."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        mock_client_class = mocker.patch("local_tavily.extract.TavilyClient")
        mock_client = mocker.MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.extract.side_effect = Exception("Extraction failed")

        result = tavily_extract("https://example.com")

        assert result["status"] == "error"
        assert "Extraction failed" in result["message"]

    def test_extract_single_url_string(self, mocker):
        """Test extraction with single URL as string."""
        mock_km = mocker.patch("local_tavily.extract.get_key_manager")
        mock_km.return_value.get_key.return_value = "test-api-key"

        mock_client_class = mocker.patch("local_tavily.extract.TavilyClient")
        mock_client = mocker.MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.extract.return_value = {"results": [], "failed_results": []}

        result = tavily_extract("https://example.com")

        assert result["status"] == "success"
        call_args = mock_client.extract.call_args.kwargs
        assert call_args["urls"] == ["https://example.com"]
