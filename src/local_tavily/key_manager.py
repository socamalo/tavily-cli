"""
API key management for Tavily with quota tracking and automatic rotation.

Keys are loaded from ~/.config/tavily/keys.json which stores:
- Per-key usage tracking
- Error history
- Disabled status
- Monthly reset tracking

Every search costs 2 points. Keys are disabled at 1000 points.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("local_tavily")

CONFIG_DIR = Path.home() / ".config" / "tavily"
CONFIG_FILE = CONFIG_DIR / "keys.json"

QUOTA_PER_KEY = 1000
POINTS_PER_SEARCH = 2


class NoAvailableKeyError(Exception):
    """Raised when all API keys are exhausted or disabled."""
    pass


class TavilyKeyManager:
    """
    Quota-based API key manager with automatic rotation.

    Keys are loaded from ~/.config/tavily/keys.json
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize key manager from config file.

        Args:
            config_path: Optional path to config file. Defaults to ~/.config/tavily/keys.json
        """
        self.config_path = config_path or CONFIG_FILE
        self._config: Dict[str, Any] = {}
        self._keys: List[Dict[str, Any]] = []
        self._dirty = False  # Track if config needs saving

        self._load_config()
        self._check_monthly_reset()

    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise ValueError(
                f"Config file not found at {self.config_path}. "
                f"Please create it with your API keys."
            )

        with open(self.config_path, "r") as f:
            self._config = json.load(f)

        self._keys = self._config.get("keys", [])
        if not self._keys:
            raise ValueError("No keys found in config file.")

        logger.info(f"Loaded {len(self._keys)} keys from {self.config_path}")

    def _save_config(self) -> None:
        """Save configuration to JSON file."""
        self._config["keys"] = self._keys

        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

        self._dirty = False

    def _check_monthly_reset(self) -> None:
        """Check if monthly reset is needed and perform it."""
        last_reset = self._config.get("last_reset_date", "")
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")

        # Parse last reset date
        if last_reset:
            try:
                last_reset_date = datetime.strptime(last_reset, "%Y-%m-%d")
                # Check if we're in a new month
                if last_reset_date.month != today.month or last_reset_date.year != today.year:
                    self._do_reset(today_str)
            except ValueError:
                # Invalid date format, do reset
                self._do_reset(today_str)
        else:
            # First time, set reset date
            self._config["last_reset_date"] = today_str
            self._dirty = True
            self._save_config()

    def _do_reset(self, today_str: str) -> None:
        """Perform the monthly reset."""
        logger.info(f"Monthly reset: clearing usage and errors for {len(self._keys)} keys")
        for key_data in self._keys:
            key_data["usage"] = 0
            key_data["errors"] = []
            # Don't clear disabled status - let it stay disabled
        self._config["last_reset_date"] = today_str
        self._dirty = True
        self._save_config()

    def get_key(self) -> str:
        """
        Get the first available API key.

        Returns:
            API key string

        Raises:
            NoAvailableKeyError: If no keys are available
        """
        for key_data in self._keys:
            if not key_data.get("disabled", False) and key_data.get("usage", 0) < QUOTA_PER_KEY:
                return key_data["key"]

        raise NoAvailableKeyError(
            f"All API keys are exhausted (usage >= {QUOTA_PER_KEY}) or disabled. "
            f"Please add more keys to {self.config_path}"
        )

    def get_all_keys_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all keys (for display purposes).

        Returns:
            List of key status dicts with name, usage, disabled, error_count
        """
        result = []
        for key_data in self._keys:
            result.append({
                "name": key_data.get("name", "unnamed"),
                "key": key_data["key"],
                "usage": key_data.get("usage", 0),
                "disabled": key_data.get("disabled", False),
                "error_count": len(key_data.get("errors", [])),
            })
        return result

    def record_usage(self, api_key: str, success: bool, error_msg: Optional[str] = None) -> None:
        """
        Record usage for an API key.

        Args:
            api_key: The API key that was used
            success: Whether the API call succeeded
            error_msg: Error message if success is False
        """
        # Find the key
        key_data = None
        for k in self._keys:
            if k["key"] == api_key:
                key_data = k
                break

        if key_data is None:
            logger.warning(f"Key not found in config: {api_key[:8]}...")
            return

        # Always add points for a search attempt
        key_data["usage"] = key_data.get("usage", 0) + POINTS_PER_SEARCH

        # Check if quota exceeded
        if key_data["usage"] >= QUOTA_PER_KEY:
            key_data["disabled"] = True
            logger.warning(f"Key {key_data.get('name', 'unnamed')} disabled (usage >= {QUOTA_PER_KEY})")

        # Record error if failed
        if not success and error_msg:
            key_data.setdefault("errors", []).append({
                "time": datetime.now().isoformat(),
                "error": error_msg,
            })

        self._dirty = True
        self._save_config()
        logger.debug(f"Recorded usage for key {key_data.get('name', 'unnamed')}: {key_data['usage']}/{QUOTA_PER_KEY}")

    def get_next_available_key(self, current_key: str) -> Optional[str]:
        """
        Get the next available key after current_key.

        Args:
            current_key: The current key that failed

        Returns:
            Next available key or None if no keys available
        """
        found_current = False
        for key_data in self._keys:
            if key_data["key"] == current_key:
                found_current = True
                continue
            if found_current:
                if not key_data.get("disabled", False) and key_data.get("usage", 0) < QUOTA_PER_KEY:
                    return key_data["key"]
        return None


# Global instance (lazy initialization)
_key_manager_instance: Optional[TavilyKeyManager] = None


def get_key_manager() -> TavilyKeyManager:
    """Get or create the key manager instance."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = TavilyKeyManager()
    return _key_manager_instance


def reset_key_manager() -> None:
    """Reset the key manager instance (for testing)."""
    global _key_manager_instance
    _key_manager_instance = None


class KeyManagerProxy:
    """Proxy to access key_manager with lazy initialization."""

    @property
    def api_key(self) -> str:
        return get_key_manager().get_key()


key_manager = KeyManagerProxy()
