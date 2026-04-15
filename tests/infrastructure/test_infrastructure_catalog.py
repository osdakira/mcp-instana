"""
Unit tests for the InfrastructureCatalogMCPTools class
"""

import asyncio
import logging
import os
import sys
import unittest
from functools import wraps
from unittest.mock import MagicMock, patch


# Create a null handler that will discard all log messages
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Configure root logger to use ERROR level and disable propagation
logging.basicConfig(level=logging.ERROR)

# Get the application logger and replace its handlers
app_logger = logging.getLogger('src.infrastructure.infrastructure_catalog')
app_logger.handlers = []
app_logger.addHandler(NullHandler())
app_logger.propagate = False  # Prevent logs from propagating to parent loggers

# Suppress traceback printing for expected test exceptions
import traceback

original_print_exception = traceback.print_exception
original_print_exc = traceback.print_exc

def custom_print_exception(etype, value, tb, limit=None, file=None, chain=True):
    # Skip printing exceptions from the mock side_effect
    if isinstance(value, Exception) and str(value) == "Test error":
        return
    original_print_exception(etype, value, tb, limit, file, chain)

def custom_print_exc(limit=None, file=None, chain=True):
    # Just do nothing - this will suppress all traceback printing from print_exc
    pass

traceback.print_exception = custom_print_exception
traceback.print_exc = custom_print_exc

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if catalog_api attribute exists, if not try to find any *_api attribute
            api_client = None
            if hasattr(self, 'catalog_api'):
                api_client = self.catalog_api
            else:
                # Find any attribute ending with '_api'
                for attr_name in dir(self):
                    if attr_name.endswith('_api'):
                        api_client = getattr(self, attr_name)
                        break

            if api_client is None:
                # Create a mock API client if none exists
                api_client = MagicMock()

            kwargs['api_client'] = api_client
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

# Create mock modules and classes
_mocks = {
    'instana_client': MagicMock(),
    'instana_client.api': MagicMock(),
    'instana_client.api.infrastructure_catalog_api': MagicMock(),
    'instana_client.configuration': MagicMock(),
    'instana_client.api_client': MagicMock(),
}

# Save original modules
_original_modules = {}
for module_name in _mocks:
    if module_name in sys.modules:
        _original_modules[module_name] = sys.modules[module_name]

# Apply mocks
for module_name, mock_obj in _mocks.items():
    sys.modules[module_name] = mock_obj

# Set up mock classes
mock_configuration = MagicMock()
mock_api_client = MagicMock()
mock_catalog_api = MagicMock()

# Add __name__ attribute to mock classes
mock_catalog_api.__name__ = "InfrastructureCatalogApi"

sys.modules['instana_client.configuration'].Configuration = mock_configuration
sys.modules['instana_client.api_client'].ApiClient = mock_api_client
sys.modules['instana_client.api.infrastructure_catalog_api'].InfrastructureCatalogApi = mock_catalog_api

# Patch the with_header_auth decorator
with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    # Import the class to test
    from src.infrastructure.infrastructure_catalog import InfrastructureCatalogMCPTools

# Clean up mocks from sys.modules to prevent interference with other tests
for module_name in _mocks:
    if module_name in _original_modules:
        # Restore original module
        sys.modules[module_name] = _original_modules[module_name]
    elif module_name in sys.modules:
        # Remove mock if there was no original
        del sys.modules[module_name]

class TestInfrastructureCatalogMCPTools(unittest.TestCase):
    """Test the InfrastructureCatalogMCPTools class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset all mocks
        mock_configuration.reset_mock()
        mock_api_client.reset_mock()
        mock_catalog_api.reset_mock()

        # Store references to the global mocks
        self.mock_configuration = mock_configuration
        self.mock_api_client = mock_api_client
        self.catalog_api = MagicMock()

        # Create the client
        self.read_token = "test_token"
        self.base_url = "https://test.instana.io"
        self.client = InfrastructureCatalogMCPTools(read_token=self.read_token, base_url=self.base_url)

        # Set up the client's API attribute
        self.client.catalog_api = self.catalog_api

        def bind_mock_api(method_name):
            original = getattr(InfrastructureCatalogMCPTools, method_name)

            @wraps(original)
            async def patched(*args, **kwargs):
                kwargs["api_client"] = self.catalog_api
                return await original(self.client, *args, **kwargs)

            setattr(self.client, method_name, patched)

        for method_name in (
            "get_available_payload_keys_by_plugin_id",
            "get_infrastructure_catalog_metrics",
            "get_infrastructure_catalog_plugins",
            "get_infrastructure_catalog_plugins_with_custom_metrics",
            "get_tag_catalog",
            "get_tag_catalog_all",
            "get_infrastructure_catalog_search_fields",
        ):
            bind_mock_api(method_name)

    def test_init(self):
        """Test that the client is initialized with the correct values"""
        self.assertEqual(self.client.read_token, self.read_token)
        self.assertEqual(self.client.base_url, self.base_url)

    def test_get_available_payload_keys_missing_plugin_id(self):
        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id=""))
        self.assertIn("error", result)
        self.assertIn("required", result["error"])

    def test_get_available_payload_keys_dict_result(self):
        mock_result = {"payload_keys": ["k1", "k2"]}
        self.catalog_api.get_available_payload_keys_by_plugin_id.return_value = mock_result

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result, mock_result)

    def test_get_available_payload_keys_list_result(self):
        self.catalog_api.get_available_payload_keys_by_plugin_id.return_value = ["k1", "k2"]

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result["payload_keys"], ["k1", "k2"])
        self.assertEqual(result["plugin_id"], "host")

    def test_get_available_payload_keys_string_result(self):
        self.catalog_api.get_available_payload_keys_by_plugin_id.return_value = "payload not available"

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="db2Database"))

        self.assertEqual(result["message"], "payload not available")
        self.assertEqual(result["plugin_id"], "db2Database")

    def test_get_available_payload_keys_fallback_json_list(self):
        response = MagicMock()
        response.status = 200
        response.data = b'["key1", "key2"]'
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result["payload_keys"], ["key1", "key2"])
        self.assertEqual(result["plugin_id"], "host")

    def test_get_available_payload_keys_fallback_non_json_string(self):
        response = MagicMock()
        response.status = 200
        response.data = b"plain text response"
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result["message"], "plain text response")
        self.assertEqual(result["plugin_id"], "host")

    def test_get_available_payload_keys_fallback_http_error(self):
        response = MagicMock()
        response.status = 500
        response.data = b""
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertIn("error", result)
        self.assertIn("HTTP 500", result["error"])

    def test_get_infrastructure_catalog_metrics_missing_plugin(self):
        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin=""))
        self.assertEqual(result, ["Error: plugin parameter is required"])

    def test_get_infrastructure_catalog_metrics_list_of_dicts(self):
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = [
            {"metricId": "cpu.usage"},
            {"label": "memory.used"},
            {"other": "value"},
        ]

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["cpu.usage", "memory.used", "{'other': 'value'}"])

    def test_get_infrastructure_catalog_metrics_to_dict_with_metrics_field_not_list(self):
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"metrics": "invalid"}
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["Metrics field is not a list for plugin host"])

    def test_get_infrastructure_catalog_metrics_to_dict_unexpected_structure(self):
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"unexpected": []}
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["Unexpected dict structure for plugin host"])

    def test_get_infrastructure_catalog_plugins_list_response(self):
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = [
            {"plugin": "host"},
            {"plugin": "jvmRuntimePlatform"},
            {"other": "ignored"},
        ]

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertEqual(result["plugins"], ["host", "jvmRuntimePlatform"])
        self.assertEqual(result["total_available"], 3)

    def test_get_infrastructure_catalog_plugins_unparseable_response(self):
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = "bad response"

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertEqual(result, {"error": "Unable to parse response"})

    def test_get_infrastructure_catalog_plugins_with_custom_metrics_list(self):
        self.catalog_api.get_infrastructure_catalog_plugins_with_custom_metrics.return_value = [
            {"plugin": "host"},
            {"plugin": "jvm"},
        ]

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins_with_custom_metrics())

        self.assertEqual(result["plugins_with_custom_metrics"], [{"plugin": "host"}, {"plugin": "jvm"}])

    def test_get_tag_catalog_missing_plugin(self):
        result = asyncio.run(self.client.get_tag_catalog(plugin=""))
        self.assertIn("error", result)
        self.assertIn("required", result["error"])

    def test_get_tag_catalog_sdk_success(self):
        mock_result = {"tags": ["host.name", "zone"]}
        self.catalog_api.get_tag_catalog.return_value = mock_result

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertEqual(result, mock_result)

    def test_get_tag_catalog_fallback_406_json(self):
        class NotAcceptableError(Exception):
            status = 406

            def __str__(self):
                return "406 Not Acceptable"

        self.catalog_api.get_tag_catalog.side_effect = NotAcceptableError()
        response = MagicMock()
        response.status = 200
        response.data = b'{"tags": ["host.name", "zone"]}'
        self.catalog_api.get_tag_catalog_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertEqual(result, {"tags": ["host.name", "zone"]})

    def test_get_tag_catalog_fallback_pydantic_error(self):
        """Test get_tag_catalog with Pydantic validation error"""
        class PydanticError(Exception):
            def __str__(self):
                return "pydantic validation error"

        self.catalog_api.get_tag_catalog.side_effect = PydanticError()
        response = MagicMock()
        response.status = 200
        response.data = b'{"tags": ["tag1"]}'
        self.catalog_api.get_tag_catalog_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertEqual(result, {"tags": ["tag1"]})

    def test_get_tag_catalog_fallback_http_error(self):
        """Test get_tag_catalog fallback with HTTP error"""
        self.catalog_api.get_tag_catalog.side_effect = Exception("406 Not Acceptable")
        response = MagicMock()
        response.status = 500
        self.catalog_api.get_tag_catalog_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertIn("error", result)
        self.assertIn("HTTP 500", result["error"])

    def test_get_tag_catalog_fallback_json_decode_error(self):
        """Test get_tag_catalog fallback with JSON decode error"""
        self.catalog_api.get_tag_catalog.side_effect = Exception("406 Not Acceptable")
        response = MagicMock()
        response.status = 200
        response.data = b"invalid json"
        self.catalog_api.get_tag_catalog_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertIn("error", result)
        self.assertIn("Failed to parse JSON", result["error"])

    def test_get_tag_catalog_non_406_error(self):
        """Test get_tag_catalog with non-406 error"""
        self.catalog_api.get_tag_catalog.side_effect = Exception("Some other error")

        result = asyncio.run(self.client.get_tag_catalog(plugin="host"))

        self.assertIn("error", result)
        self.assertIn("Failed to get tag catalog", result["error"])

    def test_get_tag_catalog_all_success(self):
        """Test get_tag_catalog_all with successful response"""
        mock_result = {
            "tagTree": [
                {
                    "label": "Infrastructure",
                    "children": [
                        {"label": "host.name"},
                        {"label": "zone"}
                    ]
                }
            ]
        }
        self.catalog_api.get_tag_catalog_all.return_value = mock_result

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("allLabels", result)
        self.assertIn("host.name", result["allLabels"])
        self.assertIn("zone", result["allLabels"])

    def test_get_tag_catalog_all_fallback(self):
        """Test get_tag_catalog_all with fallback method"""
        self.catalog_api.get_tag_catalog_all.side_effect = Exception("SDK failed")
        response = MagicMock()
        response.status = 200
        response.data = b'{"tagTree": [{"label": "Cat", "children": [{"label": "tag1"}]}]}'
        self.catalog_api.get_tag_catalog_all_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("allLabels", result)
        self.assertIn("tag1", result["allLabels"])

    def test_get_tag_catalog_all_fallback_http_error(self):
        """Test get_tag_catalog_all fallback with HTTP error"""
        self.catalog_api.get_tag_catalog_all.side_effect = Exception("SDK failed")
        response = MagicMock()
        response.status = 401
        self.catalog_api.get_tag_catalog_all_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("error", result)
        self.assertIn("Authentication failed", result["error"])

    def test_get_tag_catalog_all_fallback_403_error(self):
        """Test get_tag_catalog_all fallback with 403 error"""
        self.catalog_api.get_tag_catalog_all.side_effect = Exception("SDK failed")
        response = MagicMock()
        response.status = 403
        self.catalog_api.get_tag_catalog_all_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("error", result)
        self.assertIn("Authentication failed", result["error"])

    def test_get_tag_catalog_all_fallback_json_error(self):
        """Test get_tag_catalog_all fallback with JSON decode error"""
        self.catalog_api.get_tag_catalog_all.side_effect = Exception("SDK failed")
        response = MagicMock()
        response.status = 200
        response.data = b"invalid json"
        self.catalog_api.get_tag_catalog_all_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("error", result)
        self.assertIn("Failed to parse JSON", result["error"])

    def test_get_tag_catalog_all_exception(self):
        """Test get_tag_catalog_all with general exception"""
        self.catalog_api.get_tag_catalog_all.side_effect = Exception("Test error")
        self.catalog_api.get_tag_catalog_all_without_preload_content.side_effect = Exception("Fallback error")

        result = asyncio.run(self.client.get_tag_catalog_all())

        self.assertIn("error", result)

    def test_summarize_tag_catalog_empty(self):
        """Test _summarize_tag_catalog with empty catalog"""
        result = self.client._summarize_tag_catalog({})

        self.assertEqual(result["count"], 0)
        self.assertEqual(len(result["allLabels"]), 0)

    def test_summarize_tag_catalog_no_children(self):
        """Test _summarize_tag_catalog with categories but no children"""
        catalog = {
            "tagTree": [
                {"label": "Category1"},
                {"label": "Category2", "children": []}
            ]
        }

        result = self.client._summarize_tag_catalog(catalog)

        self.assertEqual(result["count"], 0)

    def test_summarize_tag_catalog_with_duplicates(self):
        """Test _summarize_tag_catalog removes duplicates"""
        catalog = {
            "tagTree": [
                {"label": "Cat1", "children": [{"label": "tag1"}, {"label": "tag2"}]},
                {"label": "Cat2", "children": [{"label": "tag1"}, {"label": "tag3"}]}
            ]
        }

        result = self.client._summarize_tag_catalog(catalog)

        self.assertEqual(result["count"], 3)
        self.assertIn("tag1", result["allLabels"])
        self.assertIn("tag2", result["allLabels"])
        self.assertIn("tag3", result["allLabels"])

    def test_get_infrastructure_catalog_search_fields_success(self):
        """Test get_infrastructure_catalog_search_fields with successful response"""
        mock_field1 = MagicMock()
        mock_field1.to_dict.return_value = {"keyword": "host.name"}
        mock_field2 = MagicMock()
        mock_field2.to_dict.return_value = {"keyword": "zone"}

        self.catalog_api.get_infrastructure_catalog_search_fields.return_value = [mock_field1, mock_field2]

        result = asyncio.run(self.client.get_infrastructure_catalog_search_fields())

        self.assertIn("search_fields", result)
        self.assertEqual(len(result["search_fields"]), 2)
        self.assertIn("host.name", result["search_fields"])

    def test_get_infrastructure_catalog_search_fields_with_getattr(self):
        """Test get_infrastructure_catalog_search_fields using getattr"""
        mock_field = MagicMock()
        mock_field.keyword = "test.keyword"
        delattr(mock_field, 'to_dict')

        self.catalog_api.get_infrastructure_catalog_search_fields.return_value = [mock_field]

        result = asyncio.run(self.client.get_infrastructure_catalog_search_fields())

        self.assertIn("search_fields", result)
        self.assertIn("test.keyword", result["search_fields"])

    def test_get_infrastructure_catalog_search_fields_exception(self):
        """Test get_infrastructure_catalog_search_fields with exception"""
        self.catalog_api.get_infrastructure_catalog_search_fields.side_effect = Exception("Test error")

        result = asyncio.run(self.client.get_infrastructure_catalog_search_fields())

        self.assertIn("error", result)

    def test_get_infrastructure_catalog_search_fields_skip_invalid(self):
        """Test get_infrastructure_catalog_search_fields skips invalid fields"""
        mock_field1 = MagicMock()
        mock_field1.to_dict.side_effect = Exception("Invalid")
        mock_field2 = MagicMock()
        mock_field2.to_dict.return_value = {"keyword": "valid.keyword"}

        self.catalog_api.get_infrastructure_catalog_search_fields.return_value = [mock_field1, mock_field2]

        result = asyncio.run(self.client.get_infrastructure_catalog_search_fields())

        self.assertIn("search_fields", result)
        self.assertEqual(len(result["search_fields"]), 1)
        self.assertIn("valid.keyword", result["search_fields"])

    def test_get_infrastructure_catalog_metrics_list_of_strings(self):
        """Test get_infrastructure_catalog_metrics with list of strings"""
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = ["metric1", "metric2", "metric3"]

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["metric1", "metric2", "metric3"])

    def test_get_infrastructure_catalog_metrics_to_dict_list(self):
        """Test get_infrastructure_catalog_metrics with to_dict returning list"""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = [{"metricId": "m1"}, {"metricId": "m2"}]
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["m1", "m2"])

    def test_get_infrastructure_catalog_metrics_to_dict_with_metrics(self):
        """Test get_infrastructure_catalog_metrics with metrics field"""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"metrics": [{"metricId": "m1"}, "m2"]}
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["m1", "m2"])

    def test_get_infrastructure_catalog_metrics_unexpected_type(self):
        """Test get_infrastructure_catalog_metrics with unexpected result type"""
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = 12345

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertEqual(result, ["Unexpected response format for plugin host"])

    def test_get_infrastructure_catalog_metrics_exception(self):
        """Test get_infrastructure_catalog_metrics with exception"""
        self.catalog_api.get_infrastructure_catalog_metrics.side_effect = Exception("Test error")

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        self.assertIn("Error:", result[0])

    def test_get_infrastructure_catalog_metrics_with_filter(self):
        """Test get_infrastructure_catalog_metrics with filter parameter"""
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = ["metric1"]

        asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host", filter="custom"))

        self.catalog_api.get_infrastructure_catalog_metrics.assert_called_once_with(plugin="host", filter="custom")

    def test_get_infrastructure_catalog_plugins_to_dict_list(self):
        """Test get_infrastructure_catalog_plugins with to_dict returning list"""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = [{"plugin": "p1"}, {"plugin": "p2"}]
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertEqual(result["plugins"], ["p1", "p2"])

    def test_get_infrastructure_catalog_plugins_to_dict_not_list(self):
        """Test get_infrastructure_catalog_plugins with to_dict not returning list"""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"data": "something"}
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertEqual(result, {"error": "Unexpected response format"})

    def test_get_infrastructure_catalog_plugins_with_hasattr(self):
        """Test get_infrastructure_catalog_plugins with hasattr plugin"""
        mock_item = MagicMock()
        mock_item.plugin = "test_plugin"
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = [mock_item]

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertIn("test_plugin", result["plugins"])

    def test_get_infrastructure_catalog_plugins_exception(self):
        """Test get_infrastructure_catalog_plugins with exception"""
        self.catalog_api.get_infrastructure_catalog_plugins.side_effect = Exception("Test error")

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        self.assertIn("error", result)

    def test_get_infrastructure_catalog_plugins_with_custom_metrics_dict(self):
        """Test get_infrastructure_catalog_plugins_with_custom_metrics with dict result"""
        self.catalog_api.get_infrastructure_catalog_plugins_with_custom_metrics.return_value = {"plugins": ["p1"]}

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins_with_custom_metrics())

        self.assertEqual(result, {"plugins": ["p1"]})

    def test_get_infrastructure_catalog_plugins_with_custom_metrics_to_dict(self):
        """Test get_infrastructure_catalog_plugins_with_custom_metrics with to_dict"""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"data": "test"}
        self.catalog_api.get_infrastructure_catalog_plugins_with_custom_metrics.return_value = mock_obj

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins_with_custom_metrics())

        self.assertEqual(result, {"data": "test"})

    def test_get_infrastructure_catalog_plugins_with_custom_metrics_exception(self):
        """Test get_infrastructure_catalog_plugins_with_custom_metrics with exception"""
        self.catalog_api.get_infrastructure_catalog_plugins_with_custom_metrics.side_effect = Exception("Test error")

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins_with_custom_metrics())

        self.assertIn("error", result)

    def test_get_available_payload_keys_to_dict(self):
        """Test get_available_payload_keys_by_plugin_id with to_dict"""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"keys": ["k1", "k2"]}
        self.catalog_api.get_available_payload_keys_by_plugin_id.return_value = mock_result

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result, {"keys": ["k1", "k2"]})

    def test_get_available_payload_keys_other_type(self):
        """Test get_available_payload_keys_by_plugin_id with other type"""
        self.catalog_api.get_available_payload_keys_by_plugin_id.return_value = 12345

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result["data"], "12345")

    def test_get_available_payload_keys_fallback_dict(self):
        """Test get_available_payload_keys_by_plugin_id fallback with dict"""
        response = MagicMock()
        response.status = 200
        response.data = b'{"key": "value"}'
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result, {"key": "value"})

    def test_get_available_payload_keys_fallback_other_type(self):
        """Test get_available_payload_keys_by_plugin_id fallback with other type"""
        response = MagicMock()
        response.status = 200
        response.data = b'123'
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.return_value = response

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertEqual(result["data"], 123)

    def test_get_available_payload_keys_fallback_exception(self):
        """Test get_available_payload_keys_by_plugin_id fallback with exception"""
        self.catalog_api.get_available_payload_keys_by_plugin_id.side_effect = Exception("sdk failed")
        self.catalog_api.get_available_payload_keys_by_plugin_id_without_preload_content.side_effect = Exception("fallback failed")

        result = asyncio.run(self.client.get_available_payload_keys_by_plugin_id(plugin_id="host"))

        self.assertIn("error", result)

    def test_get_infrastructure_catalog_metrics_limit_50(self):
        """Test get_infrastructure_catalog_metrics limits to 50 items"""
        # Create 60 metrics
        metrics = [f"metric{i}" for i in range(60)]
        self.catalog_api.get_infrastructure_catalog_metrics.return_value = metrics

        result = asyncio.run(self.client.get_infrastructure_catalog_metrics(plugin="host"))

        # Should be limited to 50
        self.assertEqual(len(result), 50)

    def test_get_infrastructure_catalog_plugins_limit_50(self):
        """Test get_infrastructure_catalog_plugins limits to 50 items"""
        # Create 60 plugins
        plugins = [{"plugin": f"plugin{i}"} for i in range(60)]
        self.catalog_api.get_infrastructure_catalog_plugins.return_value = plugins

        result = asyncio.run(self.client.get_infrastructure_catalog_plugins())

        # Should be limited to 50
        self.assertEqual(len(result["plugins"]), 50)
        self.assertEqual(result["total_available"], 60)


if __name__ == '__main__':
    unittest.main()
