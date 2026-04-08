"""
Tavily usage functionality.

This module provides the usage query function for the Tavily API.
"""

import json
import logging
from typing import Any, Dict, Optional

import requests

from local_tavily.key_manager import get_key_manager, QUOTA_PER_KEY

logger = logging.getLogger("local_tavily")

USAGE_API_URL = "https://api.tavily.com/usage"


def fetch_key_usage(api_key: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetch usage data for a single API key.

    Args:
        api_key: The API key to check

    Returns:
        Tuple of (success, usage_data, error_message)
        usage_data is the 'key' dict from API response, or None on failure
    """
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(USAGE_API_URL, headers=headers, timeout=30)

        if response.status_code == 200:
            try:
                usage_data = response.json()
            except json.JSONDecodeError:
                return (False, None, "Invalid JSON response from API")
            return (True, usage_data.get("key"), None)
        elif response.status_code == 401:
            return (False, None, "Invalid or missing API key (401)")
        elif response.status_code == 429:
            return (False, None, "Rate limit exceeded (429)")
        else:
            return (False, None, f"HTTP {response.status_code}")
    except requests.RequestException as e:
        return (False, None, f"Request failed: {str(e)}")


def sync_all_keys_usage() -> Dict[str, Any]:
    """
    Sync usage data for all keys from Tavily API to local config.

    Iterates all keys in keys.json, fetches usage from API for each,
    and updates local config with the results.

    Returns:
        Dict with keys: {updated: [names], failed: [(name, error)], total: int}
    """
    km = get_key_manager()
    updated = []
    failed = []

    for key_data in km._keys:
        key_name = key_data.get("name", key_data["key"][:8])
        api_key = key_data["key"]

        success, usage_data, error = fetch_key_usage(api_key)

        if success and usage_data is not None:
            api_usage = usage_data.get("usage")
            if api_usage is not None:
                key_data["usage"] = api_usage
                # Auto-enable if under quota, disable if over quota
                if api_usage < QUOTA_PER_KEY:
                    key_data["disabled"] = False
                else:
                    key_data["disabled"] = True
                # Clear errors when usage is synced (indicates reset)
                key_data["errors"] = []
                updated.append(key_name)
            # else: API returned null usage, skip
        else:
            failed.append((key_name, error or "Unknown error"))

    km._dirty = True
    km._save_config()

    return {
        "updated": updated,
        "failed": failed,
        "total": len(km._keys),
    }


def tavily_usage() -> Dict[str, Any]:
    """
    Get API usage information for the current API key.

    First syncs all keys' usage data from Tavily API, then fetches
    account data for the active key.

    Returns:
        Dictionary with usage statistics from the Tavily API.
        Includes total usage, limits, and breakdown by endpoint type.
        Always includes sync_result with keys: {updated, failed, total}.
    """
    try:
        # First, sync all keys' usage from the API
        sync_result = sync_all_keys_usage()
        logger.info(f"Synced usage for {sync_result['updated']} keys")

        api_key = get_key_manager().get_key()

        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.get(USAGE_API_URL, headers=headers, timeout=30)

        if response.status_code == 200:
            try:
                usage_data = response.json()
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "Invalid JSON response from API",
                    "sync_result": sync_result,
                }
            logger.info("Tavily usage information retrieved successfully")

            return {
                "status": "success",
                "usage": usage_data,
                "sync_result": sync_result,
            }
        elif response.status_code == 401:
            return {
                "status": "error",
                "message": "Invalid or missing API key",
                "sync_result": sync_result,
            }
        elif response.status_code == 429:
            return {
                "status": "error",
                "message": "Rate limit exceeded. Please try again later.",
                "sync_result": sync_result,
            }
        else:
            return {
                "status": "error",
                "message": f"Error fetching usage: HTTP {response.status_code}",
                "sync_result": sync_result,
            }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Required package not installed: {str(e)}",
            "sync_result": {"updated": [], "failed": [], "total": 0},
        }
    except Exception as e:
        logger.error(f"Error fetching Tavily usage: {str(e)}")
        return {
            "status": "error",
            "message": f"Error fetching Tavily usage: {str(e)}",
            "sync_result": {"updated": [], "failed": [], "total": 0},
        }
