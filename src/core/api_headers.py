"""
Utility functions for building headers for Instana API invocation.
Adapted from kubernetes-agent for MCP server use.
"""
import logging
import os
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Maximum allowed length for authentication tokens
MAX_TOKEN_LENGTH = 2048

class AuthenticationError(Exception):
    """Raised when no valid authentication credentials are provided."""
    pass

def _validate_token_length(token: str, token_type: str) -> None:
    """
    Validate that token length is within reasonable limits.

    Prevents potential attacks with excessively long tokens that could
    cause memory issues or be used to inject malicious code.

    Args:
        token: The token to validate
        token_type: Description of the token type (for error messages)

    Raises:
        ValueError: If token exceeds maximum length
    """
    if len(token) > MAX_TOKEN_LENGTH:
        logger.error(f"{token_type} exceeds maximum length: {len(token)} > {MAX_TOKEN_LENGTH}")
        raise ValueError(f"{token_type} exceeds maximum length of {MAX_TOKEN_LENGTH}")

def _validate_cookie_name(name: str) -> bool:
    """
    Validate cookie name contains only safe characters.

    Prevents cookie injection attacks by ensuring the cookie name
    only contains alphanumeric characters, hyphens, and underscores.

    Args:
        name: The cookie name to validate

    Returns:
        True if the cookie name is valid, False otherwise
    """
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))

def build_instana_api_headers(
    auth_token: Optional[str] = None,
    csrf_token: Optional[str] = None,
    api_token: Optional[str] = None,
    cookie_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Build headers for Instana API invocation.

    Supports three authentication modes with the following priority:
    1. Session Token mode (Priority 1): When auth_token and csrf_token are provided (for UI calls via coordinator)
    2. API Token mode (Priority 2): When api_token is provided (for direct API calls)
    3. Environment fallback (Priority 3): Uses INSTANA_API_TOKEN environment variable

    Args:
        auth_token: The authentication token (for cookie-based auth from UI)
        csrf_token: The CSRF token (for cookie-based auth from UI)
        api_token: The API token (for token-based auth)
        cookie_name: The cookie name for cookie-based auth (required for session-based authentication)

    Returns:
        Dictionary containing the headers needed for Instana API calls

    Raises:
        ValueError: If cookie_name is not provided for session-based authentication
        ValueError: If cookie_name contains invalid characters
        ValueError: If any token exceeds maximum length (2048 characters)
        AuthenticationError: If no valid authentication credentials are provided
    """
    # Priority 1: Use session token (auth_token and csrf_token) if both provided (UI mode via coordinator)
    if auth_token and csrf_token:
        logger.debug("Authentication method selected: session-based")

        # Validate token lengths
        _validate_token_length(auth_token, "Session auth token")
        _validate_token_length(csrf_token, "CSRF token")

        # Cookie name is required for session-based authentication
        if cookie_name is None:
            logger.error("Cookie name is required for session-based authentication")
            raise ValueError("Cookie name must be provided for session-based authentication")

        # Validate cookie name to prevent cookie injection attacks
        if not _validate_cookie_name(cookie_name):
            logger.error(f"Invalid cookie name format: {cookie_name}")
            raise ValueError("Cookie name contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed.")

        # Build the headers
        headers = {
            "X-CSRF-TOKEN": csrf_token,
            "Cookie": f"{cookie_name}={auth_token}"
        }
        return headers

    # Priority 2: Use API token if provided (direct API mode)
    if api_token:
        logger.debug("Authentication method selected: api-token")

        # Validate token length
        _validate_token_length(api_token, "API token")

        headers = {
            "Authorization": f"apiToken {api_token}"
        }
        return headers

    # Priority 3: Environment fallback - use environment variable
    api_token_env = os.getenv("INSTANA_API_TOKEN")
    if api_token_env:
        logger.debug("Authentication method selected: environment-fallback")

        # Validate token length
        _validate_token_length(api_token_env, "Environment API token")

        headers = {
            "Authorization": f"apiToken {api_token_env}"
        }
        return headers

    # No valid authentication provided
    logger.error("No valid authentication credentials provided")
    raise AuthenticationError(
        "No authentication credentials provided. Please provide either:\n"
        "1. auth_token and csrf_token for session-based auth\n"
        "2. api_token for API token auth\n"
        "3. Set INSTANA_API_TOKEN environment variable"
    )
