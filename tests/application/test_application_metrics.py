"""
Unit tests for the ApplicationMetricsMCPTools class.

Only tests for active (non-commented-out) methods are included.
Methods get_application_metrics, get_endpoints_metrics, and get_services_metrics
have been removed from source and their tests are removed accordingly.
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
app_logger = logging.getLogger('src.application.application_metrics')
app_logger.handlers = []
app_logger.addHandler(NullHandler())
app_logger.propagate = False  # Prevent logs from propagating to parent loggers

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Just pass the API client directly
            kwargs['api_client'] = self.metrics_api
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


# Set up mock classes (defined outside patch.dict so they persist after import)
mock_mcp = MagicMock()
mock_mcp_types = MagicMock()
mock_tool_annotations = MagicMock()
mock_mcp_types.ToolAnnotations = mock_tool_annotations

mock_instana_client = MagicMock()
mock_instana_api = MagicMock()
mock_app_metrics_api_mod = MagicMock()
mock_instana_configuration = MagicMock()
mock_instana_api_client = MagicMock()
mock_instana_models = MagicMock()
mock_get_app_metrics_mod = MagicMock()
mock_get_applications_mod = MagicMock()
mock_get_endpoints_mod = MagicMock()
mock_get_services_mod = MagicMock()
mock_fastmcp = MagicMock()
mock_fastmcp_server = MagicMock()
mock_fastmcp_deps = MagicMock()
mock_pydantic = MagicMock()

# Mock the get_http_headers function
mock_get_http_headers = MagicMock(return_value={})
mock_fastmcp_deps.get_http_headers = mock_get_http_headers

# Set up mock classes
mock_configuration = MagicMock()
mock_api_client = MagicMock()
mock_app_metrics_api = MagicMock()
mock_get_app_metrics = MagicMock()
mock_get_applications = MagicMock()
mock_get_endpoints = MagicMock()
mock_get_services = MagicMock()

# Add __name__ attribute to mock classes
mock_app_metrics_api.__name__ = "ApplicationMetricsApi"
mock_get_app_metrics.__name__ = "GetApplicationMetrics"
mock_get_applications.__name__ = "GetApplications"
mock_get_endpoints.__name__ = "GetEndpoints"
mock_get_services.__name__ = "GetServices"

mock_instana_configuration.Configuration = mock_configuration
mock_instana_api_client.ApiClient = mock_api_client
mock_app_metrics_api_mod.ApplicationMetricsApi = mock_app_metrics_api
mock_get_app_metrics_mod.GetApplicationMetrics = mock_get_app_metrics
mock_get_applications_mod.GetApplications = mock_get_applications
mock_get_endpoints_mod.GetEndpoints = mock_get_endpoints
mock_get_services_mod.GetServices = mock_get_services

# Mock src.prompts (needed by application_metrics.py: from src.prompts import mcp)
mock_src_prompts = MagicMock()

# Mock src.core and src.core.utils modules
mock_src_core = MagicMock()
mock_src_core_utils = MagicMock()


class MockBaseInstanaClient:
    def __init__(self, read_token: str, base_url: str):
        self.read_token = read_token
        self.base_url = base_url

    def get_headers(self, auth_token=None, csrf_token=None):
        """Mock get_headers method"""
        headers = {
            "Authorization": f"apiToken {self.read_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MCP-server/0.8.1"
        }
        if auth_token and csrf_token:
            headers["X-CSRF-TOKEN"] = csrf_token
            headers["Cookie"] = f"instanaAuthToken={auth_token}"
            del headers["Authorization"]
        return headers

    async def make_request(self, endpoint, params=None, method="GET", json=None):
        """Mock make_request method"""
        return {"data": "mock_response"}


mock_src_core_utils.BaseInstanaClient = MockBaseInstanaClient
mock_src_core_utils.register_as_tool = lambda *args, **kwargs: lambda func: func
mock_src_core_utils.with_header_auth = mock_with_header_auth

# Build the full mocks dict for patch.dict
_mocks = {
    'mcp': mock_mcp,
    'mcp.types': mock_mcp_types,
    'instana_client': mock_instana_client,
    'instana_client.api': mock_instana_api,
    'instana_client.api.application_metrics_api': mock_app_metrics_api_mod,
    'instana_client.configuration': mock_instana_configuration,
    'instana_client.api_client': mock_instana_api_client,
    'instana_client.models': mock_instana_models,
    'instana_client.models.get_application_metrics': mock_get_app_metrics_mod,
    'instana_client.models.get_applications': mock_get_applications_mod,
    'instana_client.models.get_endpoints': mock_get_endpoints_mod,
    'instana_client.models.get_services': mock_get_services_mod,
    'fastmcp': mock_fastmcp,
    'fastmcp.server': mock_fastmcp_server,
    'fastmcp.server.dependencies': mock_fastmcp_deps,
    'pydantic': mock_pydantic,
    'src.prompts': mock_src_prompts,
    'src.core': mock_src_core,
    'src.core.utils': mock_src_core_utils,
}

# Import the class under test with sys.modules mocked.
# Save original modules before mocking
_original_modules = {}
for module_name in _mocks:
    if module_name in sys.modules:
        _original_modules[module_name] = sys.modules[module_name]

# Apply mocks
for module_name, mock_obj in _mocks.items():
    sys.modules[module_name] = mock_obj

# Import with decorator patched
with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    from src.application.application_metrics import ApplicationMetricsMCPTools

# Clean up mocks from sys.modules to prevent interference with other tests
for module_name in _mocks:
    if module_name in _original_modules:
        # Restore original module
        sys.modules[module_name] = _original_modules[module_name]
    elif module_name in sys.modules:
        # Remove mock if there was no original
        del sys.modules[module_name]


class TestApplicationMetricsMCPTools(unittest.TestCase):
    """Test the ApplicationMetricsMCPTools class.

    Only tests for active methods are included. The following methods were
    removed from source and their tests are omitted:
      - get_application_metrics
      - get_endpoints_metrics
      - get_services_metrics
    """

    def setUp(self):
        """Set up test fixtures"""
        mock_configuration.reset_mock()
        mock_api_client.reset_mock()
        mock_app_metrics_api.reset_mock()

        self.mock_configuration = mock_configuration
        self.mock_api_client = mock_api_client
        self.app_metrics_api = MagicMock()

        self.read_token = "test_token"
        self.base_url = "https://test.instana.io"

        self.client = ApplicationMetricsMCPTools(read_token=self.read_token, base_url=self.base_url)
        self.client.metrics_api = self.app_metrics_api

        patcher = patch('src.application.application_metrics.logger')
        self.mock_logger = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        pass

    def test_init(self):
        """Test that the client is initialized with the correct values"""
        self.assertEqual(self.client.read_token, self.read_token)
        self.assertEqual(self.client.base_url, self.base_url)

    def test_get_application_data_metrics_v2_elicitation_when_no_params(self):
        """Test get_application_data_metrics_v2 returns elicitation_needed when called without required params.

        The method requires 'metrics' and recommends 'time_frame'. When called without
        these, it returns an elicitation_needed response instead of calling the API.
        """
        result = asyncio.run(self.client.get_application_data_metrics_v2())

        self.assertIn("elicitation_needed", result)
        self.assertTrue(result["elicitation_needed"])
        self.assertIn("missing_parameters", result)
        self.assertIn("metrics", result["missing_parameters"])

    def test_get_application_data_metrics_v2_with_params(self):
        """Test get_application_data_metrics_v2 with required parameters calls the API"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={"metrics": "test_data"})
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        metrics = [{"metric": "calls", "aggregation": "SUM"}]
        time_frame = {"from": 1000, "to": 2000}
        application_id = "app123"
        service_id = "svc456"
        endpoint_id = "ep789"

        result = asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=metrics,
            time_frame=time_frame,
            application_id=application_id,
            service_id=service_id,
            endpoint_id=endpoint_id
        ))

        self.client.metrics_api.get_application_data_metrics_v2.assert_called_once()
        self.assertEqual(result, {"metrics": "test_data"})

    def test_get_application_data_metrics_v2_error_handling(self):
        """Test get_application_data_metrics_v2 error handling when API raises exception"""
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(
            side_effect=Exception("Test error")
        )

        # Must provide required params to bypass elicitation and reach the API call
        result = asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        self.assertIn("error", result)
        self.assertIn("Failed to get application data metrics", result["error"])
        self.assertIn("Test error", result["error"])

    def test_get_application_data_metrics_v2_dict_result(self):
        """Test get_application_data_metrics_v2 with a result that's already a dict"""
        mock_result = {"metrics": "test_data"}
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        # Must provide required params to bypass elicitation and reach the API call
        result = asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        self.assertEqual(result, {"metrics": "test_data"})

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_with_items(self, mock_logger):
        """Test that logging works correctly when result has items with metrics"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "items": [
                {
                    "metrics": {
                        "calls": {
                            "values": [[1000, 10], [2000, 20], [3000, 30]],
                            "aggregation": "SUM"
                        }
                    }
                },
                {
                    "metrics": {
                        "errors": {
                            "values": [[1000, 1], [2000, 2]],
                            "aggregation": "SUM"
                        }
                    }
                }
            ]
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify logging was called
        self.assertTrue(mock_logger.info.called)
        # Check that it logged the number of items
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Number of items: 2" in str(call) for call in log_calls))
        # Check that it logged metric information
        self.assertTrue(any("calls" in str(call) for call in log_calls))
        # Check that it logged the sum
        self.assertTrue(any("SUM of all data points: 60" in str(call) for call in log_calls))

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_with_single_values(self, mock_logger):
        """Test logging when metric values are single numbers instead of [timestamp, value] pairs"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "items": [
                {
                    "metrics": {
                        "calls": {
                            "values": [10, 20, 30],  # Single values instead of pairs
                            "aggregation": "AVG"
                        }
                    }
                }
            ]
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "AVG"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify logging was called
        self.assertTrue(mock_logger.info.called)
        # Check that it logged the sum (10 + 20 + 30 = 60)
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(any("SUM of all data points: 60" in str(call) for call in log_calls))

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_with_non_numeric_values(self, mock_logger):
        """Test logging handles non-numeric values gracefully"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "items": [
                {
                    "metrics": {
                        "status": {
                            "values": ["OK", "ERROR", "OK"],  # Non-numeric values
                            "aggregation": "DISTINCT_COUNT"
                        }
                    }
                }
            ]
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "status", "aggregation": "DISTINCT_COUNT"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify logging was called and didn't crash
        self.assertTrue(mock_logger.info.called)
        # Should not have logged a sum since values are non-numeric
        [str(call) for call in mock_logger.info.call_args_list]
        # The sum logging should have been skipped due to TypeError/ValueError

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_with_empty_values(self, mock_logger):
        """Test logging when metric values list is empty"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "items": [
                {
                    "metrics": {
                        "calls": {
                            "values": [],  # Empty values list
                            "aggregation": "SUM"
                        }
                    }
                }
            ]
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify logging was called
        self.assertTrue(mock_logger.info.called)
        # Check that it logged 0 data points
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Number of data points: 0" in str(call) for call in log_calls))

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_without_items(self, mock_logger):
        """Test logging when result doesn't have items key"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "data": "some_other_format"
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify basic logging was called but not item-specific logging
        self.assertTrue(mock_logger.info.called)
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        # Should not have logged "Number of items" since there's no items key
        self.assertFalse(any("Number of items:" in str(call) for call in log_calls))

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_metric_without_values(self, mock_logger):
        """Test logging when metric doesn't have values key"""
        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={
            "items": [
                {
                    "metrics": {
                        "calls": {
                            "aggregation": "SUM"
                            # No 'values' key
                        }
                    }
                }
            ]
        })
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify logging was called
        self.assertTrue(mock_logger.info.called)
        # Should have logged aggregation but not values
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Aggregation: SUM" in str(call) for call in log_calls))

    @patch('src.application.application_metrics.logger')
    def test_get_application_data_metrics_v2_logging_first_three_items_only(self, mock_logger):
        """Test that logging only processes first 3 items even if more exist"""
        mock_result = MagicMock()
        items = [{"metrics": {"calls": {"values": [[i*1000, i]]}}} for i in range(10)]
        mock_result.to_dict = MagicMock(return_value={"items": items})
        self.client.metrics_api.get_application_data_metrics_v2 = MagicMock(return_value=mock_result)

        asyncio.run(self.client.get_application_data_metrics_v2(
            metrics=[{"metric": "calls", "aggregation": "SUM"}],
            time_frame={"from": 1000, "to": 2000}
        ))

        # Verify it logged 10 items total
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Number of items: 10" in str(call) for call in log_calls))
        # But only logged details for items 0, 1, 2 (not 3+)
        self.assertTrue(any("Item 0:" in str(call) for call in log_calls))
        self.assertTrue(any("Item 1:" in str(call) for call in log_calls))
        self.assertTrue(any("Item 2:" in str(call) for call in log_calls))
        self.assertFalse(any("Item 3:" in str(call) for call in log_calls))


if __name__ == '__main__':
    unittest.main()
