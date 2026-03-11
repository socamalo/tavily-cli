"""
Tests for the key_manager module.
"""
import os
from datetime import datetime
from unittest.mock import patch

import pytest

from local_tavily.key_manager import TavilyKeyManager, get_key_manager, key_manager


class TestTavilyKeyManager:
    """Tests for TavilyKeyManager class."""

    def test_init_with_keys_list(self):
        """Test initialization with explicit keys list."""
        keys = ["key1", "key2", "key3"]
        manager = TavilyKeyManager(keys=keys)

        assert manager.keys == keys
        assert manager.days_per_key == 11  # ceil(31/3) = 11

    def test_init_with_no_keys_raises_error(self):
        """Test that initialization with empty keys raises ValueError."""
        with pytest.raises(ValueError, match="No Tavily API keys found"):
            TavilyKeyManager(keys=[])

    def test_init_loads_from_env(self, monkeypatch):
        """Test loading keys from environment variables."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "test-key-1")
        monkeypatch.setenv("TAVILY_API_KEY_2", "test-key-2")

        manager = TavilyKeyManager()

        assert len(manager.keys) == 2
        assert manager.keys[0] == "test-key-1"
        assert manager.keys[1] == "test-key-2"

    def test_api_key_rotation(self, monkeypatch):
        """Test that API key rotates based on day of month."""
        keys = ["key1", "key2", "key3"]
        manager = TavilyKeyManager(keys=keys)

        # Day 1-11: key1
        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 5)
            assert manager.api_key == "key1"

        # Day 12-22: key2
        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15)
            assert manager.api_key == "key2"

        # Day 23-31: key3
        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 28)
            assert manager.api_key == "key3"

    def test_api_key_bounds_check(self):
        """Test that key index doesn't exceed available keys."""
        # With 2 keys and 31 days, days_per_key = 16
        keys = ["key1", "key2"]
        manager = TavilyKeyManager(keys=keys)

        # Day 31 should still return key2 (last key)
        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 31)
            assert manager.api_key == "key2"

    def test_single_key_always_returned(self):
        """Test that with a single key, it's always returned."""
        keys = ["only-key"]
        manager = TavilyKeyManager(keys=keys)

        for day in [1, 15, 31]:
            with patch('local_tavily.key_manager.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, 1, day)
                assert manager.api_key == "only-key"

    def test_keys_stripped(self, monkeypatch):
        """Test that keys are stripped of whitespace."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "  key-with-spaces  ")

        manager = TavilyKeyManager()

        assert manager.keys[0] == "key-with-spaces"


class TestGetKeyManager:
    """Tests for get_key_manager function."""

    def test_lazy_initialization(self, monkeypatch):
        """Test that key manager is lazily initialized."""
        # Clear any existing instance
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        monkeypatch.setenv("TAVILY_API_KEY_1", "lazy-key")

        # First call should initialize
        manager1 = get_key_manager()
        assert manager1.api_key == "lazy-key"

        # Second call should return same instance
        manager2 = get_key_manager()
        assert manager1 is manager2


class TestKeyManagerProxy:
    """Tests for KeyManagerProxy class."""

    def test_proxy_access(self, monkeypatch):
        """Test that key_manager proxy works."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "proxy-key")

        # Clear any existing instance
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        # Access through proxy
        assert key_manager.api_key == "proxy-key"


class TestEdgeCases:
    """Edge case tests."""

    def test_many_keys(self):
        """Test with many keys."""
        keys = [f"key{i}" for i in range(1, 32)]  # 31 keys
        manager = TavilyKeyManager(keys=keys)

        assert manager.days_per_key == 1  # ceil(31/31) = 1

        # Each day should get a different key
        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1)
            assert manager.api_key == "key1"

        with patch('local_tavily.key_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 31)
            assert manager.api_key == "key31"

    def test_consecutive_key_loading(self, monkeypatch):
        """Test that keys must be consecutive (no gaps)."""
        monkeypatch.setenv("TAVILY_API_KEY_1", "key1")
        # Skip key 2
        monkeypatch.setenv("TAVILY_API_KEY_3", "key3")

        manager = TavilyKeyManager()

        # Should only load key1, stop at gap
        assert len(manager.keys) == 1
        assert manager.keys[0] == "key1"
