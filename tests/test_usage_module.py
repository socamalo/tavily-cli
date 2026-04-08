import pytest
import requests
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


def test_sync_all_keys_usage_partial_failure():
    """Test sync handles partial failures gracefully."""
    from local_tavily.usage import sync_all_keys_usage

    with patch('local_tavily.usage.get_key_manager') as mock_km:
        mock_manager = MagicMock()
        mock_manager._keys = [
            {"key": "key1", "name": "key1", "usage": 0, "errors": [], "disabled": False},
            {"key": "key2", "name": "key2", "usage": 0, "errors": [], "disabled": False},
        ]
        mock_km.return_value = mock_manager

        def mock_fetch(key):
            if key == "key1":
                return (True, {"usage": 300}, None)
            else:
                return (False, None, "Network error")

        with patch('local_tavily.usage.fetch_key_usage', side_effect=mock_fetch):
            result = sync_all_keys_usage()
            assert result["total"] == 2
            assert result["updated"] == ["key1"]
            assert result["failed"] == [("key2", "Network error")]
            # key1 should be updated
            assert mock_manager._keys[0]["usage"] == 300
            mock_manager._save_config.assert_called_once()


def test_sync_all_keys_usage_auto_enable():
    """Test key is re-enabled when API shows usage < 1000."""
    from local_tavily.usage import sync_all_keys_usage

    with patch('local_tavily.usage.get_key_manager') as mock_km:
        mock_manager = MagicMock()
        mock_manager._keys = [
            {"key": "key1", "name": "key1", "usage": 1000, "errors": [{"time": "2026-04-01", "error": "old"}], "disabled": True},
        ]
        mock_km.return_value = mock_manager

        with patch('local_tavily.usage.fetch_key_usage', return_value=(True, {"usage": 500}, None)):
            result = sync_all_keys_usage()
            assert result["updated"] == ["key1"]
            assert mock_manager._keys[0]["disabled"] is False  # re-enabled
            assert mock_manager._keys[0]["usage"] == 500
            assert mock_manager._keys[0]["errors"] == []  # cleared
            mock_manager._save_config.assert_called_once()


def test_sync_all_keys_usage_auto_disable():
    """Test key is disabled when API shows usage >= 1000."""
    from local_tavily.usage import sync_all_keys_usage

    with patch('local_tavily.usage.get_key_manager') as mock_km:
        mock_manager = MagicMock()
        mock_manager._keys = [
            {"key": "key1", "name": "key1", "usage": 500, "errors": [], "disabled": False},
        ]
        mock_km.return_value = mock_manager

        with patch('local_tavily.usage.fetch_key_usage', return_value=(True, {"usage": 1200}, None)):
            result = sync_all_keys_usage()
            assert result["updated"] == ["key1"]
            assert mock_manager._keys[0]["disabled"] is True  # disabled
            assert mock_manager._keys[0]["usage"] == 1200
            mock_manager._save_config.assert_called_once()


def test_fetch_key_usage_network_error():
    """Test fetch_key_usage handles network errors."""
    with patch('local_tavily.usage.requests.get', side_effect=requests.RequestException("Connection refused")):
        success, data, error = fetch_key_usage("test-key")
        assert success is False
        assert data is None
        assert "Connection refused" in error


def test_tavily_usage_syncs_all_keys():
    """Test tavily_usage calls sync and returns account data."""
    from local_tavily.usage import tavily_usage

    with patch('local_tavily.usage.sync_all_keys_usage') as mock_sync, \
         patch('local_tavily.usage.get_key_manager') as mock_km:

        mock_sync.return_value = {"updated": ["key1"], "failed": [], "total": 1}

        # Mock a successful API call for the active key's account data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": {"usage": 100},
            "account": {"current_plan": "Researcher", "plan_limit": 1000}
        }

        with patch('local_tavily.usage.requests.get', return_value=mock_response):
            result = tavily_usage()
            assert result["status"] == "success"
            assert "sync_result" in result
            assert result["sync_result"]["updated"] == ["key1"]
            # Verify sync was called
            mock_sync.assert_called_once()