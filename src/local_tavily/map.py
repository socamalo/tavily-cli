"""
Tavily map functionality.

This module provides the core map function for the Tavily API
with comprehensive parameter support.
"""

import logging
from typing import Any, Dict, List, Optional

from tavily import TavilyClient

from local_tavily.key_manager import key_manager

logger = logging.getLogger("local_tavily")


def tavily_map(
    url: str,
    instructions: Optional[str] = None,
    max_depth: Optional[int] = None,
    max_breadth: Optional[int] = None,
    limit: Optional[int] = None,
    select_paths: Optional[List[str]] = None,
    select_domains: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    allow_external: bool = False,
    timeout: Optional[float] = None,
    include_usage: bool = False,
) -> Dict[str, Any]:
    """
    Map a website structure using Tavily's map API.

    Args:
        url: Root URL to map (required)
        instructions: Natural language instructions for mapping
        max_depth: Maximum map depth (1-5)
        max_breadth: Maximum breadth per level (1-500)
        limit: Total links to process
        select_paths: Regex patterns for paths to include
        select_domains: Regex patterns for domains to include
        exclude_paths: Regex patterns for paths to exclude
        exclude_domains: Regex patterns for domains to exclude
        allow_external: Allow external links
        timeout: Timeout in seconds (10-150)
        include_usage: Include usage statistics in response

    Returns:
        Dictionary with map results
    """
    try:
        logger.info(f"Executing Tavily map: {url}")
        api_key = key_manager.api_key
        client = TavilyClient(api_key=api_key)

        # Validate parameters
        if max_depth is not None and not (1 <= max_depth <= 5):
            return {
                "status": "error",
                "message": f"max_depth must be between 1 and 5, got {max_depth}",
            }

        if max_breadth is not None and not (1 <= max_breadth <= 500):
            return {
                "status": "error",
                "message": f"max_breadth must be between 1 and 500, got {max_breadth}",
            }

        if timeout is not None and not (10 <= timeout <= 150):
            return {
                "status": "error",
                "message": f"timeout must be between 10 and 150 seconds, got {timeout}",
            }

        # Prepare parameters
        params = {
            "url": url,
            "allow_external": allow_external,
        }

        # Add optional parameters
        if instructions:
            params["instructions"] = instructions

        if max_depth is not None:
            params["max_depth"] = max_depth

        if max_breadth is not None:
            params["max_breadth"] = max_breadth

        if limit is not None:
            params["limit"] = limit

        if select_paths:
            params["select_paths"] = select_paths

        if select_domains:
            params["select_domains"] = select_domains

        if exclude_paths:
            params["exclude_paths"] = exclude_paths

        if exclude_domains:
            params["exclude_domains"] = exclude_domains

        if timeout is not None:
            params["timeout"] = timeout

        if include_usage:
            params["include_usage"] = include_usage

        # Execute map
        response = client.map(**params)
        logger.info("Tavily map completed successfully")

        return {
            "status": "success",
            "results": response.get("results", []),
            "url": url,
            "response_time": response.get("response_time", 0),
            "request_id": response.get("request_id"),
            "usage": response.get("usage") if include_usage else None,
        }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Tavily Python SDK not installed: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Error during Tavily map: {str(e)}")
        return {
            "status": "error",
            "message": f"Error during Tavily map: {str(e)}",
        }
