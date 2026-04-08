import pytest
from unittest.mock import patch, MagicMock
from local_tavily.usage import fetch_key_usage

def test_fetch_key_usage_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "key": {"usage": 500, "limit": None, "search_usage": 400, "crawl_usage": 0, "extract_usage": 100}
    }

    with patch('local_tavily.usage.requests.get', return_value=mock_response):
        success, data, error = fetch_key_usage("test-key")
        assert success is True
        assert data["usage"] == 500  # Note: data IS the 'key' dict, not wrapped
        assert error is None

def test_fetch_key_usage_401():
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch('local_tavily.usage.requests.get', return_value=mock_response):
        success, data, error = fetch_key_usage("bad-key")
        assert success is False
        assert data is None
        assert "401" in error