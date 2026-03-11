"""
Tests for CLI search command.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from local_tavily.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_search(mocker):
    """Mock tavily_search function."""
    return mocker.patch("local_tavily.cli.tavily_search")


@pytest.fixture
def mock_validate(mocker):
    """Mock validate_api_key function."""
    return mocker.patch("local_tavily.cli.validate_api_key")


class TestSearchCommand:
    """Test cases for the search command."""

    def test_search_basic(self, runner, mock_search, mock_validate):
        """Test basic search with just a query."""
        mock_search.return_value = {
            "status": "success",
            "query": "Python",
            "results": [{"title": "Test", "url": "https://test.com", "score": 0.9}],
            "response_time": 1.0,
        }

        result = runner.invoke(cli, ["search", "Python"])

        assert result.exit_code == 0
        mock_search.assert_called_once()
        call_args = mock_search.call_args.kwargs
        assert call_args["query"] == "Python"
        assert call_args["search_depth"] == "basic"
        assert call_args["max_results"] == 10

    def test_search_with_depth(self, runner, mock_search, mock_validate):
        """Test search with depth option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--depth", "advanced"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["search_depth"] == "advanced"

    def test_search_with_max_results(self, runner, mock_search, mock_validate):
        """Test search with max-results option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--max-results", "5"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["max_results"] == 5

    def test_search_with_topic(self, runner, mock_search, mock_validate):
        """Test search with topic option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "news", "--topic", "news"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["topic"] == "news"

    def test_search_with_time_range(self, runner, mock_search, mock_validate):
        """Test search with time-range option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "news", "--time-range", "week"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["time_range"] == "week"

    def test_search_with_dates(self, runner, mock_search, mock_validate):
        """Test search with start-date and end-date options."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, [
            "search", "news",
            "--start-date", "2024-01-01",
            "--end-date", "2024-01-31"
        ])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["start_date"] == "2024-01-01"
        assert mock_search.call_args.kwargs["end_date"] == "2024-01-31"

    def test_search_with_days(self, runner, mock_search, mock_validate):
        """Test search with days option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "news", "--topic", "news", "--days", "7"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["days"] == 7

    def test_search_with_country(self, runner, mock_search, mock_validate):
        """Test search with country option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--country", "us"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["country"] == "us"

    def test_search_with_include_domains(self, runner, mock_search, mock_validate):
        """Test search with include-domains option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, [
            "search", "Python",
            "--include-domains", "python.org,github.com"
        ])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_domains"] == ["python.org", "github.com"]

    def test_search_with_exclude_domains(self, runner, mock_search, mock_validate):
        """Test search with exclude-domains option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, [
            "search", "Python",
            "--exclude-domains", "spam.com,ads.com"
        ])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["exclude_domains"] == ["spam.com", "ads.com"]

    def test_search_with_include_answer(self, runner, mock_search, mock_validate):
        """Test search with include-answer=true."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-answer", "true"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_answer"] is True

    def test_search_with_include_answer_false(self, runner, mock_search, mock_validate):
        """Test search with include-answer=false."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-answer", "false"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_answer"] is False

    def test_search_with_include_answer_basic(self, runner, mock_search, mock_validate):
        """Test search with include-answer=basic."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-answer", "basic"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_answer"] == "basic"

    def test_search_with_include_answer_advanced(self, runner, mock_search, mock_validate):
        """Test search with include-answer=advanced."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-answer", "advanced"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_answer"] == "advanced"

    def test_search_with_include_images(self, runner, mock_search, mock_validate):
        """Test search with include-images flag."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-images"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_images"] is True

    def test_search_with_include_image_descriptions(self, runner, mock_search, mock_validate):
        """Test search with include-image-descriptions flag."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-image-descriptions"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_image_descriptions"] is True

    def test_search_with_include_raw_content(self, runner, mock_search, mock_validate):
        """Test search with include-raw-content=true."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-raw-content", "true"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_raw_content"] is True

    def test_search_with_include_raw_content_markdown(self, runner, mock_search, mock_validate):
        """Test search with include-raw-content=markdown."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-raw-content", "markdown"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_raw_content"] == "markdown"

    def test_search_with_include_raw_content_text(self, runner, mock_search, mock_validate):
        """Test search with include-raw-content=text."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--include-raw-content", "text"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["include_raw_content"] == "text"

    def test_search_with_chunks_per_source(self, runner, mock_search, mock_validate):
        """Test search with chunks-per-source option."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--chunks-per-source", "3"])

        assert result.exit_code == 0
        assert mock_search.call_args.kwargs["chunks_per_source"] == 3

    def test_search_json_output(self, runner, mock_search, mock_validate):
        """Test search with JSON output."""
        mock_search.return_value = {"status": "success", "results": []}

        result = runner.invoke(cli, ["search", "Python", "--output", "json"])

        assert result.exit_code == 0
        assert '"status": "success"' in result.output

    def test_search_markdown_output(self, runner, mock_search, mock_validate):
        """Test search with markdown output."""
        mock_search.return_value = {
            "status": "success",
            "query": "Python",
            "results": [{"title": "Test", "url": "https://test.com", "score": 0.9}],
            "response_time": 1.0,
        }

        result = runner.invoke(cli, ["search", "Python", "--output", "markdown"])

        assert result.exit_code == 0
        assert "# Search Results: Python" in result.output

    def test_search_error(self, runner, mock_search, mock_validate):
        """Test search with error response."""
        mock_search.return_value = {
            "status": "error",
            "message": "API Error",
        }

        result = runner.invoke(cli, ["search", "Python"])

        assert result.exit_code != 0
        assert "API Error" in result.output

    def test_search_help(self, runner):
        """Test search command help."""
        result = runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search the web using Tavily" in result.output
        assert "--depth" in result.output
        assert "--max-results" in result.output
