"""
Integration tests for the CLI.

These tests verify the end-to-end flow from CLI to API calls.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from local_tavily.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestIntegration:
    """Integration test cases."""

    def test_cli_help(self, runner):
        """Test CLI help displays correctly."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Tavily Search CLI" in result.output
        assert "search" in result.output
        assert "extract" in result.output
        assert "version" in result.output
        assert "config" in result.output

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ["version"])

        assert result.exit_code == 0
        assert "Local Tavily" in result.output

    def test_config_command(self, runner, monkeypatch):
        """Test config command with mocked key manager."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "test-key-1")
        monkeypatch.setenv("TAVILY_API_KEY_2", "test-key-2")

        # Clear cached instance
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        result = runner.invoke(cli, ["config"])

        assert result.exit_code == 0
        assert "API Keys Loaded" in result.output
        assert "2" in result.output

    def test_search_help(self, runner):
        """Test search command help."""
        result = runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search the web using Tavily" in result.output
        # Check all options are documented
        assert "--depth" in result.output
        assert "--max-results" in result.output
        assert "--topic" in result.output
        assert "--time-range" in result.output
        assert "--country" in result.output
        assert "--include-domains" in result.output
        assert "--exclude-domains" in result.output
        assert "--output" in result.output

    def test_extract_help(self, runner):
        """Test extract command help."""
        result = runner.invoke(cli, ["extract", "--help"])

        assert result.exit_code == 0
        assert "Extract content from URLs" in result.output
        assert "--depth" in result.output
        assert "--format" in result.output
        assert "--output" in result.output


class TestKeyManagerToCliIntegration:
    """Integration tests between key_manager and CLI."""

    def test_cli_uses_key_manager_rotation(self, monkeypatch):
        """Test that CLI uses the key manager's rotation logic."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "rotated-key-1")
        monkeypatch.setenv("TAVILY_API_KEY_2", "rotated-key-2")

        # Clear any cached key manager instance
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        with patch("local_tavily.cli.tavily_search") as mock_search:
            mock_search.return_value = {
                "status": "success",
                "results": [],
                "query": "test",
                "response_time": 0.1
            }

            runner = CliRunner()
            result = runner.invoke(cli, ["search", "test"])

            assert result.exit_code == 0
            mock_search.assert_called_once()


class TestUtilsToToolsIntegration:
    """Integration tests between utils and search modules."""

    def test_country_normalization_in_search(self):
        """Test that country normalization works in search."""
        from local_tavily.search import tavily_search
        from local_tavily.utils import normalize_country

        # Verify that country codes used are valid
        assert normalize_country("us") == "united states"
        assert normalize_country("uk") == "united kingdom"
        assert normalize_country("cn") == "china"

        # Verify that invalid countries raise errors that search can catch
        with pytest.raises(ValueError):
            normalize_country("invalid")


class TestEndToEndWorkflows:
    """End-to-end workflow tests with mocked external APIs."""

    @patch("local_tavily.cli.tavily_search")
    def test_full_search_workflow(self, mock_search, runner, monkeypatch):
        """Test complete search workflow from CLI to API."""
        # Setup
        monkeypatch.setenv("TAVILY_API_KEY_1", "test-key")

        mock_search.return_value = {
            "status": "success",
            "results": [
                {"title": "Python", "url": "https://python.org", "score": 0.95}
            ],
            "query": "python",
            "response_time": 0.5,
            "answer": "Python is a programming language",
            "images": []
        }

        # Execute
        result = runner.invoke(cli, ["search", "python"])

        # Verify
        assert result.exit_code == 0
        assert "Python" in result.output
        mock_search.assert_called_once()

    @patch("local_tavily.cli.tavily_extract")
    def test_full_extract_workflow(self, mock_extract, runner, monkeypatch):
        """Test complete extract workflow from CLI to API."""
        # Setup
        monkeypatch.setenv("TAVILY_API_KEY_1", "test-key")

        mock_extract.return_value = {
            "status": "success",
            "results": [{"url": "https://example.com", "content": "Extracted"}],
            "failed_results": [],
            "response_time": 0.3
        }

        # Execute
        result = runner.invoke(cli, ["extract", "https://example.com"])

        # Verify
        assert result.exit_code == 0
        mock_extract.assert_called_once()


class TestErrorPropagation:
    """Tests for error propagation across modules."""

    def test_key_manager_error_to_cli(self, runner, monkeypatch):
        """Test that key manager errors are properly shown in CLI."""
        # Ensure no keys are set
        for key in list(os.environ.keys()):
            if key.startswith("TAVILY_API_KEY"):
                monkeypatch.delenv(key)

        # Clear cached instance
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        result = runner.invoke(cli, ["search", "test"])

        # Should show error about no API keys
        assert result.exit_code != 0
        assert "No Tavily API keys found" in result.output
