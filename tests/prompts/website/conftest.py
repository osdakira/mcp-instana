"""Pytest configuration for website prompts tests."""
import sys
from unittest.mock import MagicMock


def pytest_configure(config):
    """Configure pytest - runs before test collection."""
    # Create a mock FastMCP that returns a pass-through decorator for prompt()
    mock_fastmcp = MagicMock()
    mock_mcp_instance = MagicMock()

    # Make prompt() return a decorator that just returns the original function
    def mock_prompt_decorator():
        def decorator(func):
            return func
        return decorator

    mock_mcp_instance.prompt = mock_prompt_decorator
    mock_fastmcp.FastMCP.return_value = mock_mcp_instance

    # Mock keys that need to be mocked before any imports
    mocked_keys = {
        "mcp": MagicMock(),
        "fastmcp": mock_fastmcp,
        "instana_client": MagicMock(),
        "instana_client.api": MagicMock(),
        "instana_client.api.website_catalog_api": MagicMock(),
        "src.core": MagicMock(),
        "src.core.utils": MagicMock(),
    }

    for key, mock_obj in mocked_keys.items():
        if key not in sys.modules:
            sys.modules[key] = mock_obj
