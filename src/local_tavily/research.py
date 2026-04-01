"""
Tavily research functionality.

This module provides the core research functions for the Tavily API
with comprehensive parameter support.
"""

import logging
from typing import Any, Dict, Optional

from tavily import TavilyClient

from local_tavily.key_manager import get_key_manager

logger = logging.getLogger("local_tavily")


def tavily_research(
    input: str,
    model: str = "auto",
    stream: bool = False,
    output_schema: Optional[Dict[str, Any]] = None,
    citation_format: str = "numbered",
) -> Dict[str, Any]:
    """
    Create a deep research task using Tavily's research API.

    Args:
        input: Research task or question (required)
        model: Model to use - "mini", "pro", or "auto"
        stream: Use SSE streaming output
        output_schema: JSON Schema for structured output
        citation_format: Citation format - "numbered", "mla", "apa", or "chicago"

    Returns:
        Dictionary with research results or task info
    """
    try:
        logger.info(f"Executing Tavily research: {input[:50]}...")
        api_key = get_key_manager().get_key()
        client = TavilyClient(api_key=api_key)

        # Validate model
        if model not in ("mini", "pro", "auto"):
            return {
                "status": "error",
                "message": f"model must be 'mini', 'pro', or 'auto', got '{model}'",
            }

        # Validate citation_format
        if citation_format not in ("numbered", "mla", "apa", "chicago"):
            return {
                "status": "error",
                "message": f"citation_format must be 'numbered', 'mla', 'apa', or 'chicago', got '{citation_format}'",
            }

        # Prepare parameters
        params = {
            "input": input,
            "model": model,
            "stream": stream,
            "citation_format": citation_format,
        }

        # Add optional parameters
        if output_schema:
            params["output_schema"] = output_schema

        # Execute research
        response = client.research(**params)
        logger.info("Tavily research completed successfully")

        return {
            "status": "success",
            "request_id": response.get("request_id"),
            "input": input,
            "model": model,
            "response_time": response.get("response_time", 0),
            # If streaming, response will be different
            "result": response.get("result") if not stream else None,
        }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Tavily Python SDK not installed: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Error during Tavily research: {str(e)}")
        return {
            "status": "error",
            "message": f"Error during Tavily research: {str(e)}",
        }


def tavily_research_status(request_id: str) -> Dict[str, Any]:
    """
    Get the status of a research task.

    Args:
        request_id: The research task request ID

    Returns:
        Dictionary with research task status
    """
    try:
        logger.info(f"Checking Tavily research status: {request_id}")
        api_key = get_key_manager().get_key()
        client = TavilyClient(api_key=api_key)

        # Get research status
        response = client.get_research(request_id)
        logger.info("Tavily research status retrieved successfully")

        return {
            "status": "success",
            "request_id": request_id,
            "state": response.get("state"),
            "result": response.get("result"),
            "error": response.get("error"),
            "response_time": response.get("response_time", 0),
        }

    except ImportError as e:
        return {
            "status": "error",
            "message": f"Tavily Python SDK not installed: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Error getting Tavily research status: {str(e)}")
        return {
            "status": "error",
            "message": f"Error getting Tavily research status: {str(e)}",
        }
