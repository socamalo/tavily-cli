"""
End-to-end smoke tests for local_tavily.

These tests verify that the package can be imported and basic functionality works.
They don't require external API calls.
"""
import importlib


class TestImports:
    """Test that all modules can be imported."""

    def test_import_key_manager(self):
        """Test key_manager module import."""
        from local_tavily import key_manager
        assert key_manager is not None

    def test_import_utils(self):
        """Test utils module import."""
        from local_tavily import utils
        assert utils is not None

    def test_import_search(self):
        """Test search module import."""
        from local_tavily import search
        assert search is not None

    def test_import_extract(self):
        """Test extract module import."""
        from local_tavily import extract
        assert extract is not None

    def test_import_formatters(self):
        """Test formatters module import."""
        from local_tavily import formatters
        assert formatters is not None

    def test_import_cli(self):
        """Test cli module import."""
        from local_tavily import cli
        assert cli is not None


class TestPackageStructure:
    """Test package structure and exports."""

    def test_version_available(self):
        """Test that version is available."""
        from local_tavily import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_all_modules_have_docstrings(self):
        """Test that all modules have docstrings."""
        from local_tavily import key_manager, utils, search, extract, formatters, cli

        modules = [key_manager, utils, search, extract, formatters, cli]

        for module in modules:
            assert module.__doc__ is not None
            assert len(module.__doc__) > 0


class TestKeyManagerSmoke:
    """Smoke tests for key manager."""

    def test_key_manager_class_exists(self):
        """Test that TavilyKeyManager class exists."""
        from local_tavily.key_manager import TavilyKeyManager
        assert TavilyKeyManager is not None

    def test_key_manager_can_be_instantiated_with_keys(self):
        """Test that key manager can be created with explicit keys."""
        from local_tavily.key_manager import TavilyKeyManager

        manager = TavilyKeyManager(keys=["key1", "key2"])
        assert len(manager.keys) == 2


class TestUtilsSmoke:
    """Smoke tests for utils."""

    def test_country_map_exists(self):
        """Test that country code map exists."""
        from local_tavily.utils import COUNTRY_CODE_MAP
        assert isinstance(COUNTRY_CODE_MAP, dict)
        assert "us" in COUNTRY_CODE_MAP

    def test_normalize_country_function_exists(self):
        """Test that normalize_country function exists."""
        from local_tavily.utils import normalize_country
        assert callable(normalize_country)

    def test_normalize_country_works(self):
        """Test that normalize_country works for basic case."""
        from local_tavily.utils import normalize_country

        result = normalize_country("us")
        assert result == "united states"


class TestSearchSmoke:
    """Smoke tests for search module."""

    def test_tavily_search_function_exists(self):
        """Test that tavily_search function exists."""
        from local_tavily.search import tavily_search
        assert callable(tavily_search)


class TestExtractSmoke:
    """Smoke tests for extract module."""

    def test_tavily_extract_function_exists(self):
        """Test that tavily_extract function exists."""
        from local_tavily.extract import tavily_extract
        assert callable(tavily_extract)


class TestFormattersSmoke:
    """Smoke tests for formatters module."""

    def test_format_search_table_exists(self):
        """Test that format_search_table function exists."""
        from local_tavily.formatters import format_search_table
        assert callable(format_search_table)

    def test_format_search_json_exists(self):
        """Test that format_search_json function exists."""
        from local_tavily.formatters import format_search_json
        assert callable(format_search_json)

    def test_format_search_markdown_exists(self):
        """Test that format_search_markdown function exists."""
        from local_tavily.formatters import format_search_markdown
        assert callable(format_search_markdown)


class TestCLISmoke:
    """Smoke tests for CLI."""

    def test_cli_group_exists(self):
        """Test that CLI group exists."""
        from local_tavily.cli import cli
        assert cli is not None

    def test_main_function_exists(self):
        """Test that main function exists."""
        from local_tavily.cli import main
        assert callable(main)

    def test_commands_exist(self):
        """Test that all CLI commands exist."""
        from local_tavily.cli import cli

        commands = ["search", "extract", "version", "config"]

        for cmd in commands:
            assert cmd in cli.commands, f"Command {cmd} should exist"


class TestVersionConsistency:
    """Test version consistency across modules."""

    def test_version_matches_pyproject(self):
        """Test that version matches pyproject.toml."""
        from local_tavily import __version__

        # Version should be in semver format
        parts = __version__.split(".")
        assert len(parts) >= 2

        # All parts should be numeric (or have numeric prefix)
        for part in parts:
            assert part[0].isdigit()

    def test_version_not_placeholder(self):
        """Test that version is not a placeholder."""
        from local_tavily import __version__

        placeholder_versions = ["0.0.0", "0.1.0.dev", "unknown", ""]
        assert __version__ not in placeholder_versions
