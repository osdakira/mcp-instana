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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    """Mock decorator that passes through the function with api_client injected"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Inject the API client
            kwargs["api_client"] = self.analyze_api
            # Call the original function
            return await func(self, *args, **kwargs)

        # Return the wrapper, not the decorator
        return wrapper

    # Return the decorator function
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

# Mock src.application.application_utils
mock_app_utils = MagicMock()
mock_paginate_and_collect = MagicMock()
mock_app_utils.paginate_and_collect = mock_paginate_and_collect


class MockBaseInstanaClient:
    def __init__(self, read_token: str, base_url: str):
        self.read_token = read_token
        self.base_url = base_url


mock_src_core_utils.BaseInstanaClient = MockBaseInstanaClient
mock_src_core_utils.register_as_tool = lambda *args, **kwargs: lambda f: f
mock_src_core_utils.with_header_auth = mock_with_header_auth

# Build the full mocks dict for patch.dict
_mocks = {
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
    "instana_client.models.get_traces": mock_get_traces_mod,
    "instana_client.models.get_call_groups": MagicMock(),
    "src.prompts": mock_src_prompts,
    "src.core": mock_src_core,
    "src.core.utils": mock_src_core_utils,
    "src.application.application_utils": mock_app_utils,
}

# Import the class under test with sys.modules mocked
with patch.dict(sys.modules, _mocks):
    from src.application.application_analyze import ApplicationAnalyzeMCPTools


class TestApplicationAnalyzeMCPTools(unittest.TestCase):
    """Test cases for ApplicationAnalyzeMCPTools"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset all mocks
        mock_configuration.reset_mock()
        mock_api_client.reset_mock()
        mock_app_analyze_api.reset_mock()
        mock_paginate_and_collect.reset_mock()

        # Clear side_effect from previous tests
        mock_paginate_and_collect.side_effect = None

        # Store references to the global mocks
        self.mock_configuration = mock_configuration
        self.mock_api_client = mock_api_client
        self.analyze_api = MagicMock()
        self.mock_paginate = mock_paginate_and_collect

        # Create the client
        self.read_token = "test_token"
        self.base_url = "https://test.instana.io"
        self.tools = ApplicationAnalyzeMCPTools(
            read_token=self.read_token, base_url=self.base_url
        )

        # Set up the client's API attribute
        self.tools.analyze_api = self.analyze_api

    def test_get_all_traces_success(self):
        """Test successful get_all_traces with pagination"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_traces_123456.jsonl"
        mock_pager_result.item_count = 5
        mock_pager_result.file_size_bytes = 2048
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 100}},
                max_retrieval_size=100
            )
        )

        # Verify results
        self.assertIn("file_path", result)
        self.assertIn("item_count", result)
        self.assertIn("file_size_bytes", result)
        self.assertIn("stop_reason", result)
        self.assertEqual(result["item_count"], 5)
        self.assertEqual(result["stop_reason"], "all_fetched")
        self.assertIn("/tmp/instana_traces_", result["file_path"])

        # Verify paginate_and_collect was called
        self.mock_paginate.assert_called_once()

    def test_get_all_traces_with_max_retrieval_size(self):
        """Test get_all_traces with custom max_retrieval_size"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_traces_123456.jsonl"
        mock_pager_result.item_count = 500
        mock_pager_result.file_size_bytes = 10240
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run the test with max_retrieval_size=500
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 100}},
                max_retrieval_size=500
            )
        )

        # Verify results are returned as-is from paginate_and_collect
        self.assertEqual(result["item_count"], 500)
        self.assertEqual(result["stop_reason"], "all_fetched")
        self.assertEqual(result["file_path"], "/tmp/instana_traces_123456.jsonl")
        self.assertEqual(result["file_size_bytes"], 10240)

        # Verify max_retrieval_size was passed to paginate_and_collect
        call_args = self.mock_paginate.call_args
        self.assertEqual(call_args.kwargs["max_retrieval_size"], 500)

    def test_get_all_traces_with_string_payload(self):
        """Test get_all_traces with string payload"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_traces_123456.jsonl"
        mock_pager_result.item_count = 2
        mock_pager_result.file_size_bytes = 512
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run with JSON string
        result = asyncio.run(
            self.tools.get_all_traces(
                payload='{"pagination": {"retrievalSize": 50}}',
                max_retrieval_size=100
            )
        )

        # Verify results
        self.assertIn("file_path", result)
        self.assertIn("item_count", result)

    def test_get_all_traces_error_handling(self):
        """Test get_all_traces error handling"""
        # Mock paginate_and_collect to raise an exception
        self.mock_paginate.side_effect = Exception("Pagination error")

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 100}},
                max_retrieval_size=100
            )
        )

        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Failed to get traces", result["error"])

    def test_get_all_traces_default_max_retrieval_size(self):
        """Test get_all_traces uses default max_retrieval_size=200"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_traces_123456.jsonl"
        mock_pager_result.item_count = 50
        mock_pager_result.file_size_bytes = 1024
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run without specifying max_retrieval_size
        result = asyncio.run(
            self.tools.get_all_traces(payload={})
        )

        # Verify default max_retrieval_size=200 was used
        call_args = self.mock_paginate.call_args
        self.assertEqual(call_args.kwargs["max_retrieval_size"], 200)

    def test_get_trace_details_success(self):
        """Test successful get_trace_details with pagination"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_trace_details_trace123_123456.jsonl"
        mock_pager_result.item_count = 10
        mock_pager_result.file_size_bytes = 4096
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run the test
        result = asyncio.run(
            self.tools.get_trace_details(
                id="trace123",
                retrievalSize=100,
                max_retrieval_size=200
            )
        )

        # Verify results
        self.assertIn("file_path", result)
        self.assertIn("item_count", result)
        self.assertIn("file_size_bytes", result)
        self.assertIn("stop_reason", result)
        self.assertEqual(result["item_count"], 10)
        self.assertEqual(result["stop_reason"], "all_fetched")
        self.assertIn("/tmp/instana_trace_details_trace123_", result["file_path"])

        # Verify paginate_and_collect was called
        self.mock_paginate.assert_called_once()

    def test_get_trace_details_missing_id(self):
        """Test get_trace_details with missing trace ID"""
        result = asyncio.run(self.tools.get_trace_details(id=""))

        self.assertIn("error", result)
        self.assertIn("Trace ID must be provided", result["error"])

    def test_get_trace_details_invalid_retrieval_size(self):
        """Test get_trace_details with invalid retrievalSize"""
        result = asyncio.run(
            self.tools.get_trace_details(id="trace123", retrievalSize=20000)
        )

        self.assertIn("error", result)
        self.assertIn("retrievalSize must be between 1 and 10000", result["error"])

    def test_get_trace_details_with_custom_max_retrieval_size(self):
        """Test get_trace_details passes max_retrieval_size to paginate_and_collect"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_trace_details_trace123_123456.jsonl"
        mock_pager_result.item_count = 500
        mock_pager_result.file_size_bytes = 20480
        mock_pager_result.stop_reason = "limit_reached"

        self.mock_paginate.return_value = mock_pager_result

        # Run the test with max_retrieval_size=500
        result = asyncio.run(
            self.tools.get_trace_details(
                id="trace123",
                retrievalSize=100,
                max_retrieval_size=500
            )
        )

        # Verify results
        self.assertEqual(result["item_count"], 500)
        self.assertEqual(result["stop_reason"], "limit_reached")
        self.assertIn("/tmp/instana_trace_details_trace123_", result["file_path"])

        # Verify max_retrieval_size was passed to paginate_and_collect
        call_args = self.mock_paginate.call_args
        self.assertEqual(call_args.kwargs["max_retrieval_size"], 500)

    def test_get_trace_details_error_handling(self):
        """Test get_trace_details error handling"""
        # Mock paginate_and_collect to raise an exception
        self.mock_paginate.side_effect = Exception("API error")

        result = asyncio.run(
            self.tools.get_trace_details(id="trace123", max_retrieval_size=100)
        )

        self.assertIn("error", result)
        self.assertIn("Failed to get trace details", result["error"])

    def test_get_trace_details_default_max_retrieval_size(self):
        """Test get_trace_details uses default max_retrieval_size=200"""
        # Mock paginate_and_collect result
        mock_pager_result = MagicMock()
        mock_pager_result.file_path = "/tmp/instana_trace_details_trace123_123456.jsonl"
        mock_pager_result.item_count = 150
        mock_pager_result.file_size_bytes = 8192
        mock_pager_result.stop_reason = "all_fetched"

        self.mock_paginate.return_value = mock_pager_result

        # Run without specifying max_retrieval_size
        result = asyncio.run(self.tools.get_trace_details(id="trace123"))

        # Verify default max_retrieval_size=200 was used
        call_args = self.mock_paginate.call_args
        self.assertEqual(call_args.kwargs["max_retrieval_size"], 200)

if __name__ == "__main__":
    unittest.main()

# Made with Bob
