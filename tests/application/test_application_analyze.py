"""
Unit tests for the ApplicationAnalyzeMCPTools class.
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
app_logger = logging.getLogger("src.application.application_analyze")
app_logger.handlers = []
app_logger.addHandler(NullHandler())
app_logger.propagate = False

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Just pass the API client directly
            kwargs["api_client"] = self.analyze_api
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


# Set up mock classes
mock_mcp = MagicMock()
mock_mcp_types = MagicMock()
mock_tool_annotations = MagicMock()
mock_mcp_types.ToolAnnotations = mock_tool_annotations

mock_instana_client = MagicMock()
mock_instana_api = MagicMock()
mock_app_analyze_api_mod = MagicMock()
mock_instana_configuration = MagicMock()
mock_instana_api_client = MagicMock()
mock_instana_models = MagicMock()
mock_get_traces_mod = MagicMock()
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
mock_app_analyze_api = MagicMock()
mock_get_traces = MagicMock()

# Add __name__ attribute to mock classes
mock_app_analyze_api.__name__ = "ApplicationAnalyzeApi"
mock_get_traces.__name__ = "GetTraces"

mock_instana_configuration.Configuration = mock_configuration
mock_instana_api_client.ApiClient = mock_api_client
mock_app_analyze_api_mod.ApplicationAnalyzeApi = mock_app_analyze_api
mock_get_traces_mod.GetTraces = mock_get_traces

# Mock src.prompts
mock_src_prompts = MagicMock()

# Mock src.core and src.core.utils modules
mock_src_core = MagicMock()
mock_src_core_utils = MagicMock()


class MockBaseInstanaClient:
    def __init__(self, read_token: str, base_url: str):
        self.read_token = read_token
        self.base_url = base_url


mock_src_core_utils.BaseInstanaClient = MockBaseInstanaClient
mock_src_core_utils.register_as_tool = lambda *args, **kwargs: lambda f: f
mock_src_core_utils.with_header_auth = mock_with_header_auth

# Mock TagFilterExpressionElement
mock_tag_filter_element = MagicMock()
mock_tag_filter_element_mod = MagicMock()
mock_tag_filter_element_mod.TagFilterExpressionElement = mock_tag_filter_element

# Apply all mocks to sys.modules before importing the module under test
with patch.dict(
    "sys.modules",
    {
        "mcp": mock_mcp,
        "mcp.types": mock_mcp_types,
        "fastmcp": mock_fastmcp,
        "fastmcp.server": mock_fastmcp_server,
        "fastmcp.server.dependencies": mock_fastmcp_deps,
        "pydantic": mock_pydantic,
        "instana_client": mock_instana_client,
        "instana_client.api": mock_instana_api,
        "instana_client.api.application_analyze_api": mock_app_analyze_api_mod,
        "instana_client.api_client": mock_instana_api_client,
        "instana_client.configuration": mock_instana_configuration,
        "instana_client.models": mock_instana_models,
        "instana_client.models.tag_filter_expression_element": mock_tag_filter_element_mod,
        "instana_client.models.get_traces": mock_get_traces_mod,
        "instana_client.models.get_call_groups": MagicMock(),
        "instana_client.models.group": MagicMock(),
        "instana_client.models.tag_filter": MagicMock(),
        "src.prompts": mock_src_prompts,
        "src.core": mock_src_core,
        "src.core.utils": mock_src_core_utils,
    },
):
    from src.application.application_analyze import ApplicationAnalyzeMCPTools


class TestApplicationAnalyzeMCPTools(unittest.TestCase):
    """Test cases for ApplicationAnalyzeMCPTools"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset all mocks
        mock_configuration.reset_mock()
        mock_api_client.reset_mock()
        mock_app_analyze_api.reset_mock()

        # Store references to the global mocks
        self.mock_configuration = mock_configuration
        self.mock_api_client = mock_api_client
        self.analyze_api = MagicMock()

        # Create the client
        self.read_token = "test_token"
        self.base_url = "https://test.instana.io"
        self.tools = ApplicationAnalyzeMCPTools(
            read_token=self.read_token, base_url=self.base_url
        )

        # Set up the client's API attribute
        self.tools.analyze_api = self.analyze_api

    def test_get_all_traces_success(self):
        """Test successful get_all_traces with file output"""
        # Mock API response
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "items": [
                {"traceId": "trace1", "label": "Test Trace 1"},
                {"traceId": "trace2", "label": "Test Trace 2"},
            ],
            "canLoadMore": False,
        }
        self.analyze_api.get_traces.return_value = mock_result

        # Mock file operations
        with (
            patch("builtins.open", create=True) as mock_open,
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_stat.return_value.st_size = 1024

            # Run the test
            result = asyncio.run(
                self.tools.get_all_traces(
                    payload={"pagination": {"retrievalSize": 100}}
                )
            )

            # Verify results
            self.assertIn("file_path", result)
            self.assertIn("summary", result)
            self.assertEqual(result["summary"]["total_traces"], 2)
            self.assertIn("/tmp/instana_traces_", result["file_path"])

            # Verify API was called
            self.analyze_api.get_traces.assert_called_once()

    def test_get_all_traces_with_string_payload(self):
        """Test get_all_traces with string payload"""
        # Mock API response
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"items": []}
        self.analyze_api.get_traces.return_value = mock_result

        # Mock file operations
        with (
            patch("pathlib.Path.write_text"),
            patch("pathlib.Path.stat") as mock_stat,
        ):
            mock_stat.return_value.st_size = 512

            # Run with JSON string
            result = asyncio.run(
                self.tools.get_all_traces(
                    payload='{"pagination": {"retrievalSize": 50}}'
                )
            )

            # Verify results
            self.assertIn("file_path", result)
            self.assertIn("summary", result)

    def test_get_all_traces_error_handling(self):
        """Test get_all_traces error handling"""
        # Mock API to raise an exception
        self.analyze_api.get_traces.side_effect = Exception("API Error")

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(payload={"pagination": {"retrievalSize": 100}})
        )

        # Verify error response
        self.assertIn("error", result)
        self.assertIn("API Error", result["error"])

    def test_get_all_traces_pagination_multiple_pages(self):
        """Test pagination with multiple pages"""
        # Mock API responses for 3 pages
        mock_results = []
        for i in range(3):
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {
                "items": [
                    {"traceId": f"trace{i*2+1}", "timestamp": 1000 + i*2},
                    {"traceId": f"trace{i*2+2}", "timestamp": 1000 + i*2 + 1},
                ],
                "canLoadMore": i < 2,  # Last page has canLoadMore=False
            }
            mock_results.append(mock_result)

        self.analyze_api.get_traces.side_effect = mock_results

        # Mock file operations
        with (
            patch("builtins.open", create=True) as mock_open,
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_stat.return_value.st_size = 2048
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Run the test
            result = asyncio.run(
                self.tools.get_all_traces(payload={})
            )

            # Verify results
            self.assertIn("file_path", result)
            self.assertIn("summary", result)
            self.assertEqual(result["summary"]["total_traces"], 6)  # 3 pages * 2 traces
            self.assertEqual(result["summary"]["pages_fetched"], 3)
            self.assertEqual(result["metadata"]["stop_reason"], "completed")
            self.assertFalse(result["metadata"]["can_load_more"])

            # Verify API was called 3 times
            self.assertEqual(self.analyze_api.get_traces.call_count, 3)

    def test_get_all_traces_pagination_size_limit(self):
        """Test pagination stops at size limit"""
        # Create large mock data that will exceed 2MB
        large_trace = {"traceId": "trace1", "data": "x" * 1000000}  # ~1MB per trace

        mock_results = []
        for i in range(5):
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {
                "items": [large_trace],
                "canLoadMore": True,
            }
            mock_results.append(mock_result)

        self.analyze_api.get_traces.side_effect = mock_results

        # Mock file operations
        with (
            patch("builtins.open", create=True) as mock_open,
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_stat.return_value.st_size = 3000000  # 3MB
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Run the test
            result = asyncio.run(
                self.tools.get_all_traces(payload={})
            )

            # Verify size limit was hit
            self.assertEqual(result["metadata"]["stop_reason"], "size_limit")
            self.assertTrue(result["metadata"]["size_limit_reached"])
            # Should stop after 2 pages (each ~1MB)
            self.assertLessEqual(result["summary"]["pages_fetched"], 3)

    def test_get_all_traces_pagination_page_limit(self):
        """Test pagination stops at page limit"""
        # Mock API to always return canLoadMore=True
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "items": [{"traceId": "trace1", "timestamp": 1000}],
            "canLoadMore": True,
        }
        self.analyze_api.get_traces.return_value = mock_result

        # Mock file operations
        with (
            patch("builtins.open", create=True) as mock_open,
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_stat.return_value.st_size = 1024
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Run the test
            result = asyncio.run(
                self.tools.get_all_traces(payload={})
            )

            # Verify page limit was hit
            self.assertEqual(result["summary"]["pages_fetched"], 100)
            self.assertEqual(result["metadata"]["stop_reason"], "page_limit")
            self.assertTrue(result["metadata"]["page_limit_reached"])
            self.assertTrue(result["metadata"]["can_load_more"])

    def test_get_all_traces_pagination_error_cleanup(self):
        """Test that partial file is deleted on error"""
        # First call succeeds, second call fails
        mock_result1 = MagicMock()
        mock_result1.to_dict.return_value = {
            "items": [{"traceId": "trace1", "timestamp": 1000}],
            "canLoadMore": True,
        }

        self.analyze_api.get_traces.side_effect = [
            mock_result1,
            Exception("API Error on page 2")
        ]

        # Mock file operations
        with (
            patch("builtins.open", create=True) as mock_open,
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            # First exists check returns True (file exists for deletion)
            mock_exists.return_value = True
            mock_stat.return_value.st_size = 1024
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Run the test
            result = asyncio.run(
                self.tools.get_all_traces(payload={})
            )

            # Verify error response
            self.assertIn("error", result)
            self.assertIn("Failed to collect traces", result["error"])

            # Verify partial file was deleted (called within _collect_all_traces)
            self.assertTrue(mock_unlink.called)


if __name__ == "__main__":
    unittest.main()

# Made with Bob
