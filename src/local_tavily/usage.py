"""
Tavily usage functionality.

This module provides the usage query function for the Tavily API.
Note: The usage endpoint may not be available in all Tavily SDK versions.
"""

import logging
from typing import Any, Dict

from tavily import TavilyClient

from local_tavily.key_manager import get_key_manager

logger = logging.getLogger("local_tavily")


def tavily_usage() -> Dict[str, Any]:
    """
    Get API usage information for the current API key.

    Returns:
        Dictionary with usage statistics
    """
    try:
        logger.info("Fetching Tavily usage information")
        api_key = get_key_manager().get_key()
        client = TavilyClient(api_key=api_key)

        # Check if usage method exists
        if hasattr(client, 'usage'):
            # Get usage information
            response = client.usage()
            logger.info("Tavily usage information retrieved successfully")

            return {
                "status": "success",
                "usage": response,
            }
        else:
            # Usage endpoint not available in this SDK version
            return {
                "status": "error",
                "message": "Usage API is not available in the current Tavily SDK version. Please check the Tavily dashboard for usage information.",
            }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Tavily Python SDK not installed: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Error fetching Tavily usage: {str(e)}")
        return {
            "status": "error",
            "message": f"Error fetching Tavily usage: {str(e)}",
        }
