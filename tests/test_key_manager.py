"""
Tests for the key_manager module.
"""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from local_tavily.key_manager import (
    TavilyKeyManager,
    get_key_manager,
    key_manager,
    NoAvailableKeyError,
    QUOTA_PER_KEY,
    POINTS_PER_SEARCH,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "tavily"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def sample_config(temp_config_dir):
    """Create a sample config file."""
    config = {
        "version": 1,
        "last_reset_date": "2026-04-01",
        "keys": [
            {
                "key": "test-key-1",
                "name": "key1",
                "usage": 0,
                "errors": [],
                "disabled": False,
            },
            {
                "key": "test-key-2",
                "name": "key2",
                "usage": 500,
                "errors": [],
                "disabled": False,
            },
        ],
    }
    config_file = temp_config_dir / "keys.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file


class TestTavilyKeyManager:
    """Tests for TavilyKeyManager class."""

    def test_init_loads_config(self, sample_config):
        """Test initialization loads from config file."""
        manager = TavilyKeyManager(config_path=sample_config)
        assert len(manager._keys) == 2

    def test_init_file_not_found(self, tmp_path):
        """Test that missing config file raises ValueError."""
        with pytest.raises(ValueError, match="Config file not found"):
            TavilyKeyManager(config_path=tmp_path / "nonexistent.json")

    def test_init_no_keys_in_config(self, temp_config_dir):
        """Test that empty keys raises ValueError."""
        config = {
            "version": 1,
            "last_reset_date": "2026-04-01",
            "keys": [],
        }
        config_file = temp_config_dir / "keys.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        with pytest.raises(ValueError, match="No keys found"):
            TavilyKeyManager(config_path=config_file)

    def test_get_key_returns_first_available(self, sample_config):
        """Test get_key returns first non-disabled key."""
        manager = TavilyKeyManager(config_path=sample_config)
        assert manager.get_key() == "test-key-1"

    def test_get_key_skips_disabled(self, sample_config):
        """Test get_key skips disabled keys."""
        # Update config to disable first key
        with open(sample_config, "r") as f:
            config = json.load(f)
        config["keys"][0]["disabled"] = True
        with open(sample_config, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=sample_config)
        assert manager.get_key() == "test-key-2"

    def test_get_key_skips_exhausted(self, sample_config):
        """Test get_key skips keys with usage >= quota."""
        # Update config to exhaust first key
        with open(sample_config, "r") as f:
            config = json.load(f)
        config["keys"][0]["usage"] = 1000
        with open(sample_config, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=sample_config)
        assert manager.get_key() == "test-key-2"

    def test_get_key_raises_when_all_exhausted(self, sample_config):
        """Test NoAvailableKeyError when all keys exhausted."""
        # Exhaust all keys
        with open(sample_config, "r") as f:
            config = json.load(f)
        config["keys"][0]["usage"] = 1000
        config["keys"][1]["usage"] = 1000
        with open(sample_config, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=sample_config)
        with pytest.raises(NoAvailableKeyError):
            manager.get_key()

    def test_record_usage_adds_points(self, sample_config):
        """Test record_usage adds points to key."""
        manager = TavilyKeyManager(config_path=sample_config)
        manager.record_usage("test-key-1", success=True)

        with open(sample_config, "r") as f:
            config = json.load(f)
        assert config["keys"][0]["usage"] == POINTS_PER_SEARCH

    def test_record_usage_disables_at_quota(self, sample_config):
        """Test key is disabled when usage >= quota."""
        # Set usage just under quota
        with open(sample_config, "r") as f:
            config = json.load(f)
        config["keys"][0]["usage"] = QUOTA_PER_KEY - POINTS_PER_SEARCH
        with open(sample_config, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=sample_config)
        manager.record_usage("test-key-1", success=True)

        with open(sample_config, "r") as f:
            config = json.load(f)
        assert config["keys"][0]["disabled"] is True
        assert config["keys"][0]["usage"] >= QUOTA_PER_KEY

    def test_record_usage_records_error(self, sample_config):
        """Test record_usage records error message."""
        manager = TavilyKeyManager(config_path=sample_config)
        manager.record_usage("test-key-1", success=False, error_msg="rate limit")

        with open(sample_config, "r") as f:
            config = json.load(f)
        assert len(config["keys"][0]["errors"]) == 1
        assert config["keys"][0]["errors"][0]["error"] == "rate limit"

    def test_get_next_available_key(self, sample_config):
        """Test get_next_available_key returns next key."""
        manager = TavilyKeyManager(config_path=sample_config)
        next_key = manager.get_next_available_key("test-key-1")
        assert next_key == "test-key-2"

    def test_get_next_available_key_returns_none_when_last(self, sample_config):
        """Test get_next_available_key returns None for last key."""
        manager = TavilyKeyManager(config_path=sample_config)
        next_key = manager.get_next_available_key("test-key-2")
        assert next_key is None

    def test_get_next_available_key_skips_disabled(self, sample_config):
        """Test get_next_available_key skips disabled keys."""
        # Disable second key
        with open(sample_config, "r") as f:
            config = json.load(f)
        config["keys"][1]["disabled"] = True
        with open(sample_config, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=sample_config)
        next_key = manager.get_next_available_key("test-key-1")
        assert next_key is None

    def test_monthly_reset_triggers(self, temp_config_dir):
        """Test that monthly reset triggers when month changes."""
        # Create config with last month
        config = {
            "version": 1,
            "last_reset_date": "2026-03-01",  # Last month
            "keys": [
                {
                    "key": "test-key-1",
                    "name": "key1",
                    "usage": 500,
                    "errors": [{"time": "2026-03-15T10:00:00", "error": "test"}],
                    "disabled": False,
                },
            ],
        }
        config_file = temp_config_dir / "keys.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        manager = TavilyKeyManager(config_path=config_file)

        # Usage should be reset
        with open(config_file, "r") as f:
            config = json.load(f)
        assert config["keys"][0]["usage"] == 0
        assert config["keys"][0]["errors"] == []
        assert config["last_reset_date"] == datetime.now().strftime("%Y-%m-%d")

    def test_get_all_keys_status(self, sample_config):
        """Test get_all_keys_status returns correct info."""
        manager = TavilyKeyManager(config_path=sample_config)
        status = manager.get_all_keys_status()

        assert len(status) == 2
        assert status[0]["name"] == "key1"
        assert status[0]["usage"] == 0
        assert status[0]["disabled"] is False
        assert status[0]["error_count"] == 0
        assert status[1]["usage"] == 500


class TestGetKeyManager:
    """Tests for get_key_manager function."""

    def test_lazy_initialization(self, tmp_path):
        """Test that key manager is lazily initialized."""
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        # Create a temp config dir with no config file
        # so initialization will fail
        km.CONFIG_FILE = tmp_path / "nonexistent.json"

        with pytest.raises(ValueError, match="Config file not found"):
            get_key_manager()


class TestKeyManagerProxy:
    """Tests for KeyManagerProxy class."""

    def test_proxy_access(self, sample_config):
        """Test that key_manager proxy works with mocked manager."""
        import local_tavily.key_manager as km
        km._key_manager_instance = None

        # Create a mock manager
        mock_manager = TavilyKeyManager(config_path=sample_config)
        km._key_manager_instance = mock_manager

        # Access through proxy
        assert key_manager.api_key == "test-key-1"
