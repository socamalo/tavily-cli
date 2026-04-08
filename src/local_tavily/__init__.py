"""
Local Tavily CLI - AI-powered web search from the command line.

This package provides a command-line interface for Tavily search,
extraction, crawling, mapping, research, and usage capabilities.
"""

__version__ = "0.4.5"
__author__ = "Local Tavily Team"

from local_tavily.key_manager import TavilyKeyManager, get_key_manager, NoAvailableKeyError
from local_tavily.utils import normalize_country, COUNTRY_CODE_MAP, VALID_TAVILY_COUNTRIES
from local_tavily.search import tavily_search
from local_tavily.extract import tavily_extract
from local_tavily.crawl import tavily_crawl
from local_tavily.map import tavily_map
from local_tavily.research import tavily_research, tavily_research_status
from local_tavily.usage import tavily_usage

__all__ = [
    "__version__",
    "TavilyKeyManager",
    "get_key_manager",
    "NoAvailableKeyError",
    "normalize_country",
    "COUNTRY_CODE_MAP",
    "VALID_TAVILY_COUNTRIES",
    "tavily_search",
    "tavily_extract",
    "tavily_crawl",
    "tavily_map",
    "tavily_research",
    "tavily_research_status",
    "tavily_usage",
]
