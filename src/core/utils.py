"""
Base Instana API Client Module

This module provides the base client for interacting with the Instana API.
"""

import sys
from functools import wraps
from typing import Any, Callable, Dict, Union

import requests

# Import MCP dependencies
from fastmcp import Context
from mcp.types import ToolAnnotations

# Import for getting package version from meta data rather than server.py
try:
    from importlib.metadata import version
    __version__ = version("mcp-instana")
except Exception:
    # Fallback version if package metadata is not available
    __version__ = "0.9.6"

# Registry to store all tools
MCP_TOOLS = {}

def register_as_tool(title=None, annotations=None):
    """
    Enhanced decorator that registers both in MCP_TOOLS and with @mcp.tool

    Args:
        title: Title for the MCP tool (optional, defaults to function name)
        annotations: ToolAnnotations for the MCP tool (optional)
    """
    def decorator(func):
        # Get function metadata
        func_name = func.__name__

        # Use provided title or generate from function name
        tool_title = title or func_name.replace('_', ' ').title()

        # Use provided annotations or default
        tool_annotations = annotations or ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False
        )

        # Store the metadata for later use by the server
        func._mcp_title = tool_title
        func._mcp_annotations = tool_annotations

        # Register in MCP_TOOLS (existing functionality)
        MCP_TOOLS[func_name] = func

        return func

    return decorator

def _validate_http_headers(instana_token, instana_base_url):
    """Validate HTTP mode headers."""
    if not instana_token or not instana_base_url:
        missing = []
        if not instana_token:
            missing.append("instana-api-token")
        if not instana_base_url:
            missing.append("instana-base-url")
        error_msg = f"HTTP mode detected but missing required headers: {', '.join(missing)}"
        print(f" {error_msg}", file=sys.stderr)
        return {"error": error_msg}

    if not instana_base_url.startswith("http://") and not instana_base_url.startswith("https://"):
        error_msg = "Instana base URL must start with http:// or https://"
        print(f" {error_msg}", file=sys.stderr)
        return {"error": error_msg}

    return None


def _create_api_client_from_config(base_url, api_token):
    """Create API client from configuration."""
    from instana_client.api_client import ApiClient
    from instana_client.configuration import Configuration

    configuration = Configuration()
    configuration.host = base_url
    configuration.api_key['ApiKeyAuth'] = api_token
    configuration.api_key_prefix['ApiKeyAuth'] = 'apiToken'

    api_client_instance = ApiClient(configuration=configuration)
    user_agent_value = f"MCP-server/{__version__}"
    api_client_instance.set_default_header("User-Agent", header_value=user_agent_value)

    return api_client_instance


def _try_http_mode_auth(api_class):
    """Attempt HTTP mode authentication."""
    try:
        from fastmcp.server.dependencies import get_http_headers
        headers = get_http_headers()

        instana_token = headers.get("instana-api-token")
        instana_base_url = headers.get("instana-base-url")

        # Check if we're in HTTP mode
        if not (instana_token or instana_base_url):
            return None

        # Validate headers
        validation_error = _validate_http_headers(instana_token, instana_base_url)
        if validation_error:
            return validation_error

        # Create API client
        api_client_instance = _create_api_client_from_config(instana_base_url, instana_token)
        return api_class(api_client=api_client_instance)

    except (ImportError, AttributeError) as e:
        print(f"Header detection failed, using STDIO mode: {e}", file=sys.stderr)
        return None


def _validate_stdio_credentials(self):
    """Validate STDIO mode credentials."""
    if not self.read_token or not self.base_url:
        error_msg = "Authentication failed: Missing credentials "
        if not self.read_token:
            error_msg += " - INSTANA_API_TOKEN is missing"
        if not self.base_url:
            error_msg += " - INSTANA_BASE_URL is missing"
        print(f" {error_msg}", file=sys.stderr)
        return {"error": error_msg}
    return None


def _find_existing_api_client(self, api_class):
    """Find existing API client in self attributes."""
    api_class_name = getattr(api_class, '__name__', str(api_class))
    for attr_name in dir(self):
        if attr_name.endswith('_api'):
            attr = getattr(self, attr_name)
            if hasattr(attr, '__class__') and attr.__class__.__name__ == api_class_name:
                print(f"🔐 Found existing API client: {attr_name}", file=sys.stderr)
                return getattr(self, attr_name)
    return None


def _create_stdio_api_client(self, api_class):
    """Create new API client using STDIO credentials."""
    print(" Creating new API client with constructor credentials", file=sys.stderr)
    api_client_instance = _create_api_client_from_config(self.base_url, self.read_token)
    print(f"✅ Set User-Agent header: MCP-server/{__version__}", file=sys.stderr)
    return api_class(api_client=api_client_instance)


def _auth_check_mock(allow_mock, kwargs):
    """Check if mock client should be used."""
    if allow_mock and kwargs.get('api_client') is not None:
        print(" Using mock client for testing", file=sys.stderr)
        return True
    return False


def _auth_try_http(api_class):
    """Try HTTP mode authentication and return (api_instance, error)."""
    api_instance = _try_http_mode_auth(api_class)
    if isinstance(api_instance, dict) and "error" in api_instance:
        return None, api_instance
    return api_instance, None


def _auth_try_stdio(self, api_class):
    """Try STDIO mode authentication and return (api_instance, error)."""
    print(" Using constructor-based authentication (STDIO mode)", file=sys.stderr)
    print(f" self.base_url: {self.base_url}", file=sys.stderr)

    validation_error = _validate_stdio_credentials(self)
    if validation_error:
        return None, validation_error

    api_instance = _find_existing_api_client(self, api_class)
    if not api_instance:
        api_instance = _create_stdio_api_client(self, api_class)

    return api_instance, None


async def _auth_wrapper_logic(func, self, args, kwargs, api_class, allow_mock):
    """Execute authentication logic for the wrapper function."""
    # Check for mock client
    if _auth_check_mock(allow_mock, kwargs):
        return await func(self, *args, **kwargs)

    # Try HTTP mode first
    api_instance, error = _auth_try_http(api_class)
    if error:
        return error

    if api_instance:
        kwargs['api_client'] = api_instance
        return await func(self, *args, **kwargs)

    # Fall back to STDIO mode
    api_instance, error = _auth_try_stdio(self, api_class)
    if error:
        return error

    kwargs['api_client'] = api_instance
    return await func(self, *args, **kwargs)


def with_header_auth(api_class, allow_mock=True):
    """
    Universal decorator for Instana MCP tools that provides flexible authentication.

    This decorator automatically handles authentication for any Instana API tool method.
    It supports both HTTP mode (using headers) and STDIO mode (using environment variables),
    with strict mode separation to prevent cross-mode fallbacks.

    Features:
    - HTTP Mode: Extracts credentials from HTTP headers (fails if missing)
    - STDIO Mode: Uses constructor-based authentication (fails if missing)
    - Mock Mode: Allows injection of mock clients for testing (when allow_mock=True)

    Args:
        api_class: The Instana API class to instantiate (e.g., InfrastructureTopologyApi,
                  ApplicationMetricsApi, InfrastructureCatalogApi, etc.)
        allow_mock: If True, allows mock clients to be passed directly (for testing). Defaults to True.

    Usage:
        from typing import Any, Optional
        from fastmcp import Context

        @with_header_auth(YourApiClass)
        async def your_tool_method(self, param1, param2, ctx: Optional[Context] = None, api_client: Any = None):
            # The decorator automatically injects 'api_client' into the method
            result = api_client.your_api_method(param1, param2)
            return self._convert_to_dict(result)

    Note: Always type-annotate both 'ctx' (with Optional[Context]) and 'api_client' (with Any)
    to exclude them from the published schema. These are internal parameters injected by the decorator.
    """
    def decorator(func: Callable) -> Callable:
        import inspect
        sig = inspect.signature(func)

        new_params = [
            param for name, param in sig.parameters.items()
            if name not in ('api_client',)
        ]

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await _auth_wrapper_logic(func, self, args, kwargs, api_class, allow_mock)
            except Exception as e:
                print(f"Error in header auth decorator: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                error_msg = f"Authentication error: {e}" if isinstance(e, str) else f"Authentication error: {e!s}"
                return {"error": error_msg}

        wrapper.__signature__ = sig.replace(parameters=new_params)
        return wrapper

    return decorator
class BaseInstanaClient:
    """Base client for Instana API with common functionality."""

    def __init__(self, read_token: str, base_url: str):
        self.read_token = read_token
        self.base_url = base_url

    def get_headers(self):
        """Get standard headers for Instana API requests."""
        return {
            "Authorization": f"apiToken {self.read_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"MCP-server/{__version__}",
        }

    async def make_request(self, endpoint: str, params: Union[Dict[str, Any], None] = None, method: str = "GET", json: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Make a request to the Instana API."""
        if endpoint is None:
            return {"error": "Endpoint cannot be None"}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.get_headers()

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, verify=False)
            elif method.upper() == "POST":
                # Use the json parameter if provided, otherwise use params
                data_to_send = json if json is not None else params
                response = requests.post(url, headers=headers, json=data_to_send, verify=False)
            elif method.upper() == "PUT":
                data_to_send = json if json is not None else params
                response = requests.put(url, headers=headers, json=data_to_send, verify=False)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params, verify=False)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}", file=sys.stderr)
            return {"error": f"HTTP Error: {err}"}
        except requests.exceptions.RequestException as err:
            print(f"Error: {err}", file=sys.stderr)
            return {"error": f"Error: {err}"}
        except Exception as e:
            print(f"Unexpected error: {e!s}", file=sys.stderr)
            return {"error": f"Unexpected error: {e!s}"}
