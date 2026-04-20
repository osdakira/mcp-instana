"""
Tests for settings custom dashboard tools.
"""

import asyncio
import importlib
import os
import sys
import unittest
from functools import wraps
from unittest.mock import MagicMock, patch

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            kwargs["api_client"] = self.custom_dashboards_api
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


# Create mock modules and classes BEFORE importing
sys.modules['instana_client'] = MagicMock()
sys.modules['instana_client.api'] = MagicMock()
sys.modules['instana_client.api.custom_dashboards_api'] = MagicMock()
sys.modules['instana_client.models'] = MagicMock()
sys.modules['instana_client.models.custom_dashboard'] = MagicMock()

mock_custom_dashboards_api_class = MagicMock()
mock_custom_dashboard_class = MagicMock()
mock_custom_dashboards_api_class.__name__ = "CustomDashboardsApi"
mock_custom_dashboard_class.__name__ = "CustomDashboard"

sys.modules['instana_client.api.custom_dashboards_api'].CustomDashboardsApi = mock_custom_dashboards_api_class
sys.modules['instana_client.models.custom_dashboard'].CustomDashboard = mock_custom_dashboard_class

with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    from src.settings.custom_dashboard_tools import CustomDashboardMCPTools


class TestSettingsCustomDashboardMCPTools(unittest.TestCase):
    """Coverage tests for settings custom dashboard tools."""

    def setUp(self):
        self.custom_dashboards_api = MagicMock()
        self.client = CustomDashboardMCPTools(
            read_token="test_token",
            base_url="https://test.instana.com"
        )
        self.client.custom_dashboards_api = self.custom_dashboards_api

    def test_initialization(self):
        self.assertEqual(self.client.read_token, "test_token")
        self.assertEqual(self.client.base_url, "https://test.instana.com")

    def test_get_custom_dashboards_list_trimmed(self):
        self.custom_dashboards_api.get_custom_dashboards.return_value = [
            {"id": f"dash{i}"} for i in range(15)
        ]

        result = asyncio.run(self.client.get_custom_dashboards())

        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 10)

    def test_get_custom_dashboards_dict_passthrough(self):
        self.custom_dashboards_api.get_custom_dashboards.return_value = {"items": [{"id": "dash1"}]}

        result = asyncio.run(self.client.get_custom_dashboards())

        self.assertEqual(result["items"][0]["id"], "dash1")

    def test_get_custom_dashboards_other_type_wrapped(self):
        self.custom_dashboards_api.get_custom_dashboards.return_value = "raw-result"

        result = asyncio.run(self.client.get_custom_dashboards())

        self.assertEqual(result, {"result": "raw-result"})

    def test_get_custom_dashboards_exception(self):
        self.custom_dashboards_api.get_custom_dashboards.side_effect = Exception("API Error")

        result = asyncio.run(self.client.get_custom_dashboards())

        self.assertIn("error", result)
        self.assertIn("API Error", result["error"])

    def test_get_custom_dashboard_missing_id(self):
        result = asyncio.run(self.client.get_custom_dashboard(dashboard_id=""))
        self.assertEqual(result["error"], "Dashboard ID is required for this operation")

    def test_get_custom_dashboard_to_dict(self):
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "dash1"}
        self.custom_dashboards_api.get_custom_dashboard.return_value = mock_result

        result = asyncio.run(self.client.get_custom_dashboard(dashboard_id="dash1"))

        self.custom_dashboards_api.get_custom_dashboard.assert_called_once_with(dashboard_id="dash1")
        self.assertEqual(result["id"], "dash1")

    def test_get_custom_dashboard_other_type_wrapped(self):
        self.custom_dashboards_api.get_custom_dashboard.return_value = "dashboard"

        result = asyncio.run(self.client.get_custom_dashboard(dashboard_id="dash1"))

        self.assertEqual(result, {"result": "dashboard"})

    def test_add_custom_dashboard_missing_payload(self):
        result = asyncio.run(self.client.add_custom_dashboard(custom_dashboard={}))
        self.assertIn("error", result)

    def test_add_custom_dashboard_success(self):
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "created"}
        self.custom_dashboards_api.add_custom_dashboard.return_value = mock_result

        result = asyncio.run(
            self.client.add_custom_dashboard(custom_dashboard={"title": "Test"})
        )

        self.assertEqual(result["id"], "created")
        self.custom_dashboards_api.add_custom_dashboard.assert_called_once()

    def test_add_custom_dashboard_exception(self):
        self.custom_dashboards_api.add_custom_dashboard.side_effect = Exception("add failed")

        result = asyncio.run(
            self.client.add_custom_dashboard(custom_dashboard={"title": "Test"})
        )

        self.assertIn("error", result)
        self.assertIn("add failed", result["error"])

    def test_update_custom_dashboard_missing_id(self):
        result = asyncio.run(
            self.client.update_custom_dashboard(dashboard_id="", custom_dashboard={"title": "Test"})
        )

        self.assertEqual(result["error"], "Dashboard ID is required for this operation")

    def test_update_custom_dashboard_missing_payload(self):
        result = asyncio.run(
            self.client.update_custom_dashboard(dashboard_id="dash1", custom_dashboard={})
        )

        self.assertEqual(result["error"], "Custom dashboard configuration is required for this operation")

    def test_update_custom_dashboard_success(self):
        self.custom_dashboards_api.update_custom_dashboard.return_value = {"updated": True}

        result = asyncio.run(
            self.client.update_custom_dashboard(
                dashboard_id="dash1",
                custom_dashboard={"title": "Updated"}
            )
        )

        self.assertEqual(result, {"updated": True})

    def test_delete_custom_dashboard_missing_id(self):
        result = asyncio.run(self.client.delete_custom_dashboard(dashboard_id=""))
        self.assertEqual(result["error"], "Dashboard ID is required for this operation")

    def test_delete_custom_dashboard_success(self):
        self.custom_dashboards_api.delete_custom_dashboard.return_value = {"deleted": True}

        result = asyncio.run(self.client.delete_custom_dashboard(dashboard_id="dash1"))

        self.assertEqual(result, {"deleted": True})

    def test_get_shareable_users_missing_id(self):
        result = asyncio.run(self.client.get_shareable_users(dashboard_id=""))
        self.assertEqual(result["error"], "Dashboard ID is required for this operation")

    def test_get_shareable_users_list_trimmed(self):
        self.custom_dashboards_api.get_shareable_users.return_value = [
            {"id": f"user{i}"} for i in range(25)
        ]

        result = asyncio.run(self.client.get_shareable_users(dashboard_id="dash1"))

        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 20)

    def test_get_shareable_users_dict_passthrough(self):
        self.custom_dashboards_api.get_shareable_users.return_value = {"items": [{"id": "user1"}]}

        result = asyncio.run(self.client.get_shareable_users(dashboard_id="dash1"))

        self.assertEqual(result["items"][0]["id"], "user1")

    def test_get_shareable_users_other_type_wrapped(self):
        self.custom_dashboards_api.get_shareable_users.return_value = "users"

        result = asyncio.run(self.client.get_shareable_users(dashboard_id="dash1"))

        self.assertEqual(result, {"result": "users"})

    def test_get_shareable_users_json_logging_type_error(self):
        class Unserializable:
            pass

        self.custom_dashboards_api.get_shareable_users.return_value = {"items": [Unserializable()]}

        result = asyncio.run(self.client.get_shareable_users(dashboard_id="dash1"))

        self.assertIn("items", result)

    def test_get_shareable_users_exception(self):
        self.custom_dashboards_api.get_shareable_users.side_effect = Exception("user failure")

        result = asyncio.run(self.client.get_shareable_users(dashboard_id="dash1"))

        self.assertIn("error", result)
        self.assertIn("user failure", result["error"])

    def test_get_shareable_api_tokens_missing_id(self):
        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id=""))
        self.assertEqual(result["error"], "Dashboard ID is required for this operation")

    def test_get_shareable_api_tokens_list_trimmed(self):
        self.custom_dashboards_api.get_shareable_api_tokens.return_value = [
            {"id": f"token{i}"} for i in range(15)
        ]

        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id="dash1"))

        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 10)

    def test_get_shareable_api_tokens_dict_passthrough(self):
        self.custom_dashboards_api.get_shareable_api_tokens.return_value = {"items": [{"id": "token1"}]}

        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id="dash1"))

        self.assertEqual(result["items"][0]["id"], "token1")

    def test_get_shareable_api_tokens_other_type_wrapped(self):
        self.custom_dashboards_api.get_shareable_api_tokens.return_value = "tokens"

        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id="dash1"))

        self.assertEqual(result, {"result": "tokens"})

    def test_get_shareable_api_tokens_json_logging_type_error(self):
        class Unserializable:
            pass

        self.custom_dashboards_api.get_shareable_api_tokens.return_value = {"items": [Unserializable()]}

        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id="dash1"))

        self.assertIn("items", result)

    def test_get_shareable_api_tokens_exception(self):
        self.custom_dashboards_api.get_shareable_api_tokens.side_effect = Exception("token failure")

        result = asyncio.run(self.client.get_shareable_api_tokens(dashboard_id="dash1"))

        self.assertIn("error", result)
        self.assertIn("token failure", result["error"])



if __name__ == "__main__":
    unittest.main()
