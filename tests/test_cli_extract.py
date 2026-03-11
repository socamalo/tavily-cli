"""
Tests for CLI extract command.
"""

import pytest
from click.testing import CliRunner

from local_tavily.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_extract(mocker):
    """Mock tavily_extract function."""
    return mocker.patch("local_tavily.cli.tavily_extract")


@pytest.fixture
def mock_validate(mocker):
    """Mock validate_api_key function."""
    return mocker.patch("local_tavily.cli.validate_api_key")


class TestExtractCommand:
    """Test cases for the extract command."""

    def test_extract_single_url(self, runner, mock_extract, mock_validate):
        """Test extract with a single URL."""
        mock_extract.return_value = {
            "status": "success",
            "results": [{"url": "https://example.com", "content": "Test content"}],
            "failed_results": [],
        }

        result = runner.invoke(cli, ["extract", "https://example.com"])

        assert result.exit_code == 0
        mock_extract.assert_called_once()
        call_args = mock_extract.call_args.kwargs
        assert call_args["urls"] == ["https://example.com"]

    def test_extract_multiple_urls(self, runner, mock_extract, mock_validate):
        """Test extract with multiple URLs."""
        mock_extract.return_value = {
            "status": "success",
            "results": [],
            "failed_results": [],
        }

        result = runner.invoke(cli, [
            "extract",
            "https://example.com",
            "https://test.com"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["urls"] == [
            "https://example.com",
            "https://test.com"
        ]

    def test_extract_with_depth(self, runner, mock_extract, mock_validate):
        """Test extract with depth option."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--depth", "advanced"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["extract_depth"] == "advanced"

    def test_extract_with_format(self, runner, mock_extract, mock_validate):
        """Test extract with format option."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--format", "text"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["format"] == "text"

    def test_extract_with_include_images(self, runner, mock_extract, mock_validate):
        """Test extract with include-images flag."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--include-images"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["include_images"] is True

    def test_extract_with_include_favicon(self, runner, mock_extract, mock_validate):
        """Test extract with include-favicon flag."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--include-favicon"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["include_favicon"] is True

    def test_extract_with_timeout(self, runner, mock_extract, mock_validate):
        """Test extract with timeout option."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--timeout", "30"
        ])

        assert result.exit_code == 0
        assert mock_extract.call_args.kwargs["timeout"] == 30.0

    def test_extract_json_output(self, runner, mock_extract, mock_validate):
        """Test extract with JSON output."""
        mock_extract.return_value = {"status": "success", "results": [], "failed_results": []}

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--output", "json"
        ])

        assert result.exit_code == 0
        assert '"status": "success"' in result.output

    def test_extract_markdown_output(self, runner, mock_extract, mock_validate):
        """Test extract with markdown output."""
        mock_extract.return_value = {
            "status": "success",
            "results": [{"url": "https://example.com", "content": "Test"}],
            "failed_results": [],
        }

        result = runner.invoke(cli, [
            "extract", "https://example.com",
            "--output", "markdown"
        ])

        assert result.exit_code == 0
        assert "# Extracted Content" in result.output

    def test_extract_error(self, runner, mock_extract, mock_validate):
        """Test extract with error response."""
        mock_extract.return_value = {
            "status": "error",
            "message": "Extraction failed",
        }

        result = runner.invoke(cli, ["extract", "https://example.com"])

        assert result.exit_code != 0
        assert "Extraction failed" in result.output

    def test_extract_too_many_urls(self, runner, mock_extract, mock_validate):
        """Test extract with too many URLs."""
        urls = [f"https://site{i}.com" for i in range(21)]

        result = runner.invoke(cli, ["extract"] + urls)

        assert result.exit_code != 0
        assert "Maximum 20 URLs" in result.output

    def test_extract_help(self, runner):
        """Test extract command help."""
        result = runner.invoke(cli, ["extract", "--help"])

        assert result.exit_code == 0
        assert "Extract content from URLs" in result.output
        assert "--depth" in result.output
