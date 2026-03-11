"""
Shared fixtures for tests.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_tavily_client(mocker):
    """Mock TavilyClient for testing."""
    mock_client_class = mocker.patch("local_tavily.search.TavilyClient")
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    return mock_client


@pytest.fixture
def mock_key_manager(mocker):
    """Mock key manager for testing."""
    mock = mocker.patch("local_tavily.search.key_manager")
    mock.api_key = "test-api-key"
    return mock


@pytest.fixture
def mock_extract_key_manager(mocker):
    """Mock key manager for extract testing."""
    mock = mocker.patch("local_tavily.extract.key_manager")
    mock.api_key = "test-api-key"
    return mock


@pytest.fixture
def sample_search_response():
    """Sample search response from Tavily API."""
    return {
        "status": "success",
        "query": "Python programming",
        "results": [
            {
                "title": "Python.org",
                "url": "https://python.org",
                "content": "Python is a programming language.",
                "score": 0.95,
            },
            {
                "title": "Python Tutorial",
                "url": "https://tutorial.python.org",
                "content": "Learn Python programming.",
                "score": 0.85,
            },
        ],
        "response_time": 1.5,
        "answer": "Python is a popular programming language.",
        "images": [],
        "request_id": "test-request-id",
    }


@pytest.fixture
def sample_extract_response():
    """Sample extract response from Tavily API."""
    return {
        "status": "success",
        "results": [
            {
                "url": "https://example.com",
                "content": "# Example\nThis is example content.",
                "raw_content": "<h1>Example</h1><p>This is example content.</p>",
            }
        ],
        "failed_results": [],
        "response_time": 0.8,
        "request_id": "test-request-id",
    }


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear Tavily API key environment variables before each test."""
    # Store original values
    original_keys = {}
    for key in list(os.environ.keys()):
        if key.startswith("TAVILY_API_KEY"):
            original_keys[key] = os.environ.pop(key)

    yield

    # Restore original values
    for key, value in original_keys.items():
        os.environ[key] = value
