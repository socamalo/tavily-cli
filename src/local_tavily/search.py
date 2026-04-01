"""
Tavily search functionality.

This module provides the core search function for the Tavily API
with comprehensive parameter support.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from tavily import TavilyClient

from local_tavily.key_manager import get_key_manager, NoAvailableKeyError
from local_tavily.utils import normalize_country

logger = logging.getLogger("local_tavily")


def tavily_search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 10,
    topic: str = "general",
    days: Optional[int] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    chunks_per_source: Optional[int] = None,
    include_answer: Union[bool, str] = True,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_raw_content: Union[bool, str] = False,
    include_favicon: bool = False,
    country: Optional[str] = None,
    timeout: int = 60,
    auto_parameters: bool = False,
    exact_match: bool = False,
    include_usage: bool = False,
) -> Dict[str, Any]:
    """
    Search the web using Tavily's AI search engine.

    Args:
        query: Search query text
        search_depth: "basic", "advanced", "fast", or "ultra-fast"
        max_results: Maximum number of results (0-20)
        topic: "general", "news", or "finance"
        days: Number of days back for results (only with topic="news")
        time_range: "day", "week", "month", or "year"
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
        chunks_per_source: Number of chunks per source (1-3, advanced depth only)
        include_answer: Include AI-generated answer (bool, or "basic"/"advanced")
        include_images: Include images in results
        include_image_descriptions: Include image descriptions
        include_raw_content: Include raw content (bool, or "markdown"/"text")
        include_favicon: Include website favicons
        country: Country code (e.g., "us", "uk", "cn")
        timeout: Request timeout in seconds
        auto_parameters: Automatically configure search parameters
        exact_match: Use exact matching for search query
        include_usage: Include usage statistics in response

    Returns:
        Dictionary with search results
    """
    try:
        logger.info(f"Executing Tavily search: {query}")
        key_manager_instance = get_key_manager()
        api_key = key_manager_instance.get_key()
        client = TavilyClient(api_key=api_key)

        # Validate max_results range (0-20 according to API docs)
        if not (0 <= max_results <= 20):
            return {
                "status": "error",
                "message": f"max_results must be between 0 and 20, got {max_results}",
            }

        # Validate include_domains limit (max 300)
        if include_domains is not None and len(include_domains) > 300:
            return {
                "status": "error",
                "message": f"include_domains can have at most 300 items, got {len(include_domains)}",
            }

        # Validate exclude_domains limit (max 150)
        if exclude_domains is not None and len(exclude_domains) > 150:
            return {
                "status": "error",
                "message": f"exclude_domains can have at most 150 items, got {len(exclude_domains)}",
            }

        # Validate search_depth
        valid_depths = ["basic", "advanced", "fast", "ultra-fast"]
        if search_depth not in valid_depths:
            return {
                "status": "error",
                "message": f"search_depth must be one of {valid_depths}, got '{search_depth}'",
            }

        # Validate chunks_per_source range
        if chunks_per_source is not None:
            if not (1 <= chunks_per_source <= 3):
                return {
                    "status": "error",
                    "message": f"chunks_per_source must be between 1 and 3, got {chunks_per_source}",
                }

        # Validate include_answer
        if isinstance(include_answer, str):
            if include_answer not in ("basic", "advanced"):
                return {
                    "status": "error",
                    "message": f"include_answer as string must be 'basic' or 'advanced', got '{include_answer}'",
                }

        # Validate include_raw_content
        if isinstance(include_raw_content, str):
            if include_raw_content not in ("markdown", "text"):
                return {
                    "status": "error",
                    "message": f"include_raw_content as string must be 'markdown' or 'text', got '{include_raw_content}'",
                }

        # Prepare parameters
        params = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
            "include_favicon": include_favicon,
            "timeout": timeout,
            "auto_parameters": auto_parameters,
            "exact_match": exact_match,
        }

        # Handle include_answer - can be bool or string enum
        if isinstance(include_answer, bool):
            params["include_answer"] = include_answer
        else:
            params["include_answer"] = True  # Enable answer with specified type
            params["answer_type"] = include_answer

        # Handle include_raw_content - can be bool or string enum
        if isinstance(include_raw_content, bool):
            params["include_raw_content"] = include_raw_content
        else:
            params["include_raw_content"] = True  # Enable raw content with specified format
            params["raw_content_format"] = include_raw_content

        # Add optional parameters only if they are provided
        if topic:
            params["topic"] = topic

        if days is not None and days > 0:
            params["days"] = days

        if time_range:
            params["time_range"] = time_range

        if start_date:
            params["start_date"] = start_date

        if end_date:
            params["end_date"] = end_date

        if include_domains:
            params["include_domains"] = include_domains

        if exclude_domains:
            params["exclude_domains"] = exclude_domains

        # chunks_per_source is only available with "advanced" depth
        if chunks_per_source is not None and search_depth == "advanced":
            params["chunks_per_source"] = chunks_per_source

        if country and topic == "general":
            try:
                normalized_country = normalize_country(country)
            except ValueError as ve:
                return {"status": "error", "message": str(ve)}
            if normalized_country:
                params["country"] = normalized_country

        if include_usage:
            params["include_usage"] = include_usage

        # Execute search
        response = client.search(**params)
        logger.info("Tavily search completed successfully")

        # Record successful usage
        key_manager_instance.record_usage(api_key, success=True)

        return {
            "status": "success",
            "results": response.get("results", []),
            "query": response.get("query", query),
            "response_time": response.get("response_time", 0),
            "answer": response.get("answer"),
            "images": response.get("images", []),
            "request_id": response.get("request_id"),
            "usage": response.get("usage") if include_usage else None,
            "auto_parameters": response.get("auto_parameters"),
        }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Tavily Python SDK not installed: {str(e)}",
        }
    except Exception as e:
        # Record failed usage
        key_manager_instance.record_usage(api_key, success=False, error_msg=str(e))
        logger.error(f"Error during Tavily search: {str(e)}")

        # Try next key if available
        next_key = key_manager_instance.get_next_available_key(api_key)
        if next_key:
            logger.info(f"Retrying with next key...")
            return tavily_search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                topic=topic,
                days=days,
                time_range=time_range,
                start_date=start_date,
                end_date=end_date,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                chunks_per_source=chunks_per_source,
                include_answer=include_answer,
                include_images=include_images,
                include_image_descriptions=include_image_descriptions,
                include_raw_content=include_raw_content,
                include_favicon=include_favicon,
                country=country,
                timeout=timeout,
                auto_parameters=auto_parameters,
                exact_match=exact_match,
                include_usage=include_usage,
            )

        return {
            "status": "error",
            "message": f"Error during Tavily search: {str(e)}",
        }
