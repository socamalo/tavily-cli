"""
API key management for Tavily with automatic rotation.

This module provides the TavilyKeyManager class which handles loading multiple
API keys from environment variables and rotating them based on the day of the month.
"""

import logging
import os
from datetime import datetime
from math import ceil
from typing import List, Optional

logger = logging.getLogger("local_tavily")

# Add your Tavily API keys here, or set TAVILY_API_KEY_1, TAVILY_API_KEY_2, etc. in environment.
# Get keys from https://tavily.com
DEFAULT_API_KEYS = []


class TavilyKeyManager:
    """
    Date-based API key manager with automatic rotation.

    Automatically detects the number of keys from environment variables and
    distributes them evenly across the days of the month.
    """

    def __init__(self, keys: Optional[List[str]] = None):
        """
        Initialize key manager by loading keys from environment variables.

        Args:
            keys: Optional list of API keys. If provided, uses these instead of loading from env.
                  Useful for testing.
        """
        if keys is not None:
            self.keys = keys
        else:
            self.keys = self._load_keys()

        if not self.keys:
            raise ValueError(
                "No Tavily API keys found. Please set TAVILY_API_KEY_1, TAVILY_API_KEY_2, etc. "
                "in your environment, or add them to src/local_tavily/key_manager.py"
            )

        # Calculate days per key for rotation
        # Distribute 31 days (max days in a month) across available keys
        self.days_per_key = ceil(31 / len(self.keys))
        logger.info(
            f"Loaded {len(self.keys)} Tavily API keys. Rotation: {self.days_per_key} days per key"
        )

    def _load_keys(self) -> List[str]:
        """Load Tavily API keys from environment variables or default list."""
        # First try to load from environment variables: TAVILY_API_KEY_1, TAVILY_API_KEY_2, etc.
        keys = []
        index = 1
        while True:
            key = os.getenv(f"TAVILY_API_KEY_{index}")
            if not key:
                break
            keys.append(key.strip())
            index += 1

        if keys:
            logger.info(f"Loaded {len(keys)} API key(s) from environment variables")
            return keys

        # Fallback to default keys defined in this file
        if DEFAULT_API_KEYS:
            logger.info(f"Loaded {len(DEFAULT_API_KEYS)} API key(s) from defaults")
            return [k.strip() for k in DEFAULT_API_KEYS if k and k.strip()]

        return keys

    @property
    def api_key(self) -> str:
        """Get API key based on current day of the month."""
        day = datetime.now().day
        # Calculate key index: (day - 1) // days_per_key
        # This distributes days evenly across available keys
        key_index = (day - 1) // self.days_per_key
        # Ensure index doesn't exceed available keys (for months with 31 days)
        key_index = min(key_index, len(self.keys) - 1)
        return self.keys[key_index]


# Initialize the key manager lazily to avoid import-time errors during testing
_key_manager_instance: Optional[TavilyKeyManager] = None


def get_key_manager() -> TavilyKeyManager:
    """Get or create the key manager instance (lazy initialization)."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = TavilyKeyManager()
    return _key_manager_instance


# For backward compatibility, create a property-like accessor
class KeyManagerProxy:
    """Proxy to access key_manager with lazy initialization."""

    @property
    def api_key(self) -> str:
        return get_key_manager().api_key


key_manager = KeyManagerProxy()
