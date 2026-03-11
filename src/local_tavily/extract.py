"""
Tavily extract functionality.

This module provides the core extract function for the Tavily API
with comprehensive parameter support.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from tavily import TavilyClient

from local_tavily.key_manager import key_manager

logger = logging.getLogger("local_tavily")


def tavily_extract(
    urls: Union[str, List[str]],
    extract_depth: str = "basic",
    include_images: bool = False,
    format: str = "markdown",
    timeout: Optional[float] = None,
    include_favicon: bool = False,
    query: Optional[str] = None,
    chunks_per_source: Optional[int] = None,
    include_usage: bool = False,
) -> Dict[str, Any]:
    """
    Extract content from specified URLs using Tavily.

    Args:
        urls: Single URL string OR list of URL strings (max 20 URLs)
        extract_depth: "basic" or "advanced"
        include_images: Extract image URLs from pages
        format: Output format, "markdown" or "text"
        timeout: Timeout in seconds for each URL (1.0-60.0)
        include_favicon: Include website favicon URLs
        query: Query for reranking extracted content (requires chunks_per_source)
        chunks_per_source: Number of chunks per source (1-5, only when query is provided)
        include_usage: Include usage statistics in response

    Returns:
        Dictionary with extraction results
    """
    try:
        api_key = key_manager.api_key
        client = TavilyClient(api_key=api_key)

        # Handle case when urls is a single string
        if isinstance(urls, str):
            urls = [urls]

        # Validate URL count
        if len(urls) > 20:
            return {
                "status": "error",
                "message": f"Maximum 20 URLs allowed per extraction request, got {len(urls)}",
            }

        # Validate chunks_per_source
        if chunks_per_source is not None:
            if not (1 <= chunks_per_source <= 5):
                return {
                    "status": "error",
                    "message": f"chunks_per_source must be between 1 and 5, got {chunks_per_source}",
                }
            if query is None:
                return {
                    "status": "error",
                    "message": "chunks_per_source requires a query parameter",
                }

        # Prepare parameters
        extract_params = {
            "urls": urls,
            "extract_depth": extract_depth,
            "include_images": include_images,
            "format": format,
            "include_favicon": include_favicon,
        }

        # Add timeout if specified
        if timeout:
            extract_params["timeout"] = timeout

        # Add query and chunks_per_source if specified
        if query:
            extract_params["query"] = query
            if chunks_per_source is not None:
                extract_params["chunks_per_source"] = chunks_per_source

        if include_usage:
            extract_params["include_usage"] = include_usage

        # Execute the extraction
        response = client.extract(**extract_params)

        return {
            "status": "success",
            "results": response.get("results", []),
            "failed_results": response.get("failed_results", []),
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
        logger.error(f"Error during Tavily extract: {str(e)}")
        return {
            "status": "error",
            "message": f"Error during Tavily extract: {str(e)}",
        }
