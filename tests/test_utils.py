"""
Tests for the utils module.
"""
import pytest

from local_tavily.utils import (
    COUNTRY_CODE_MAP,
    VALID_TAVILY_COUNTRIES,
    normalize_country,
)


class TestNormalizeCountry:
    """Tests for normalize_country function."""

    def test_valid_country_codes(self):
        """Test normalization of valid country codes."""
        # ISO codes
        assert normalize_country("us") == "united states"
        assert normalize_country("US") == "united states"
        assert normalize_country("uk") == "united kingdom"
        assert normalize_country("cn") == "china"
        assert normalize_country("de") == "germany"

    def test_valid_full_names(self):
        """Test normalization of full country names."""
        assert normalize_country("united states") == "united states"
        assert normalize_country("United States") == "united states"
        assert normalize_country("CHINA") == "china"
        assert normalize_country("Germany") == "germany"

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        assert normalize_country("  us  ") == "united states"
        assert normalize_country("  united states  ") == "united states"

    def test_invalid_country_raises_error(self):
        """Test that invalid country raises ValueError."""
        with pytest.raises(ValueError, match="Invalid country"):
            normalize_country("invalid-country")

        with pytest.raises(ValueError, match="Invalid country"):
            normalize_country("xx")

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert normalize_country("") is None

    def test_none_returns_none(self):
        """Test that None returns None."""
        assert normalize_country(None) is None

    def test_extended_country_codes(self):
        """Test extended country code mappings."""
        # Test some extended mappings
        assert normalize_country("usa") == "united states"
        assert normalize_country("uae") == "united arab emirates"
        assert normalize_country("jp") == "japan"
        assert normalize_country("kr") == "south korea"

    def test_all_valid_countries_accepted(self):
        """Test that all valid Tavily countries are accepted."""
        for country in VALID_TAVILY_COUNTRIES:
            result = normalize_country(country)
            assert result in VALID_TAVILY_COUNTRIES

    def test_case_insensitive_full_names(self):
        """Test that full country names are case-insensitive."""
        test_cases = [
            ("United States", "united states"),
            ("UNITED STATES", "united states"),
            ("united STATES", "united states"),
        ]
        for input_val, expected in test_cases:
            assert normalize_country(input_val) == expected


class TestCountryCodeMap:
    """Tests for COUNTRY_CODE_MAP."""

    def test_map_contains_common_codes(self):
        """Test that map contains common country codes."""
        common_codes = ["us", "uk", "cn", "de", "fr", "jp", "in", "br"]
        for code in common_codes:
            assert code in COUNTRY_CODE_MAP

    def test_map_values_are_valid(self):
        """Test that all mapped values are valid Tavily countries."""
        for value in COUNTRY_CODE_MAP.values():
            assert value in VALID_TAVILY_COUNTRIES


class TestValidTavilyCountries:
    """Tests for VALID_TAVILY_COUNTRIES set."""

    def test_contains_major_countries(self):
        """Test that major countries are in the valid set."""
        major_countries = [
            "united states",
            "united kingdom",
            "china",
            "germany",
            "france",
            "japan",
            "india",
            "brazil",
            "canada",
            "australia",
        ]
        for country in major_countries:
            assert country in VALID_TAVILY_COUNTRIES

    def test_all_lowercase(self):
        """Test that all valid countries are lowercase."""
        for country in VALID_TAVILY_COUNTRIES:
            assert country == country.lower()


class TestEdgeCases:
    """Edge case tests."""

    def test_unicode_input(self):
        """Test handling of unicode input."""
        with pytest.raises(ValueError):
            normalize_country("日本")

    def test_numeric_input(self):
        """Test handling of numeric input."""
        with pytest.raises(ValueError):
            normalize_country("123")

    def test_special_characters(self):
        """Test handling of special characters."""
        with pytest.raises(ValueError):
            normalize_country("us@123")

    def test_partial_match(self):
        """Test that partial matches don't work."""
        with pytest.raises(ValueError):
            normalize_country("united")  # Should require full "united states"

    def test_alternative_spellings(self):
        """Test alternative spellings."""
        # Some countries have alternative abbreviations
        assert normalize_country("usa") == "united states"
        assert normalize_country("uae") == "united arab emirates"
