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

    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists')
    def test_get_all_traces_success(self, mock_exists, mock_stat, mock_open):
        """Test successful get_all_traces with file output"""
        # Mock file operations
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 2048

        # Mock API response
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "items": [
                {"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}},
                {"id": 2, "cursor": {"ingestionTime": 100, "offset": 1}}
            ],
            "canLoadMore": False,
            "totalHits": 2
        }
        self.analyze_api.get_traces.return_value = mock_result

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 100}}
            )
        )

        # Verify results
        self.assertIn("filePath", result)
        self.assertIn("itemCount", result)
        self.assertIn("fileSizeBytes", result)
        self.assertIn("canLoadMore", result)
        self.assertIn("totalHits", result)
        self.assertEqual(result["itemCount"], 2)
        self.assertEqual(result["canLoadMore"], False)
        self.assertEqual(result["totalHits"], 2)
        self.assertIn("/tmp/instana_traces_", result["filePath"])

    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists')
    def test_get_all_traces_with_cursor(self, mock_exists, mock_stat, mock_open):
        """Test get_all_traces returns cursor when more data available"""
        # Mock file operations
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 4096

        # Mock API response with canLoadMore=True
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "items": [
                {"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}},
                {"id": 2, "cursor": {"ingestionTime": 100, "offset": 1}}
            ],
            "canLoadMore": True,
            "totalHits": 100
        }
        self.analyze_api.get_traces.return_value = mock_result

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 2}}
            )
        )

        # Verify results
        self.assertEqual(result["canLoadMore"], True)
        self.assertIn("ingestionTime", result)
        self.assertIn("offset", result)
        self.assertEqual(result["ingestionTime"], 100)
        self.assertEqual(result["offset"], 1)

    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists')
    def test_get_all_traces_with_string_payload(self, mock_exists, mock_stat, mock_open):
        """Test get_all_traces with string payload"""
        # Mock file operations
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 512

        # Mock API response
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "items": [{"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}}],
            "canLoadMore": False,
            "totalHits": 1
        }
        self.analyze_api.get_traces.return_value = mock_result

        # Run with JSON string
        result = asyncio.run(
            self.tools.get_all_traces(
                payload='{"pagination": {"retrievalSize": 50}}'
            )
        )

        # Verify results
        self.assertIn("filePath", result)
        self.assertIn("itemCount", result)
        self.assertEqual(result["itemCount"], 1)

    def test_get_all_traces_error_handling(self):
        """Test get_all_traces error handling"""
        # Mock API to raise an exception
        self.analyze_api.get_traces.side_effect = Exception("API error")

        # Run the test
        result = asyncio.run(
            self.tools.get_all_traces(
                payload={"pagination": {"retrievalSize": 100}}
            )
        )

        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Failed to get traces", result["error"])


if __name__ == "__main__":
    unittest.main()

# Made with Bob
