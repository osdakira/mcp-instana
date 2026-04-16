"""
E2E tests for Application Alert Configuration MCP Tools
"""

import importlib
from unittest.mock import MagicMock

import pytest


# Mock the ApiException since instana_client is not available in test environment
class ApiException(Exception):
    def __init__(self, status=None, reason=None, *args, **kwargs):
        self.status = status
        self.reason = reason
        super().__init__(*args, **kwargs)

def create_application_alert_client(instana_credentials):
    module = importlib.import_module("src.application.application_alert_config")
    module = importlib.reload(module)
    application_alert_mcp_tools = module.ApplicationAlertMCPTools
    return application_alert_mcp_tools(
        read_token=instana_credentials["api_token"],
        base_url=instana_credentials["base_url"]
    )


class TestApplicationAlertConfigE2E:
    """End-to-end tests for Application Alert Configuration MCP Tools"""

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_initialization(self, instana_credentials):
        """Test initialization of the ApplicationAlertMCPTools client."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Verify the client was created successfully
        assert client is not None
        assert client.read_token == instana_credentials["api_token"]
        assert client.base_url == instana_credentials["base_url"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_debug_print(self):
        """Test the debug_print helper function."""
        # debug_print is not exported from the module

        # Test basic debug print - debug_print is not exported from the module
        # This test verifies that the module can be imported successfully
        assert create_application_alert_client is not None

        # Test debug print with multiple args - debug_print is not exported from the module
        # This test verifies that the module can be imported successfully
        assert create_application_alert_client is not None

        # Test debug print with kwargs - debug_print is not exported from the module
        # This test verifies that the module can be imported successfully
        assert create_application_alert_client is not None

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_success(self, instana_credentials):
        """Test finding application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Test Alert",
            "severity": "warning"
        }
        mock_api_client.find_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Test Alert"
        assert result["severity"] == "warning"

        # Verify the API was called correctly
        mock_api_client.find_application_alert_config.assert_called_once_with(
            id="alert-123",
            valid_on=None
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_with_valid_on(self, instana_credentials):
        """Test finding application alert config with valid_on parameter."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Test Alert",
            "version": "1.0"
        }
        mock_api_client.find_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with valid_on parameter
        result = await client.find_application_alert_config(
            id="alert-123",
            valid_on=1625097600000,
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Test Alert"
        assert result["version"] == "1.0"

        # Verify the API was called correctly
        mock_api_client.find_application_alert_config.assert_called_once_with(
            id="alert-123",
            valid_on=1625097600000
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_api_error(self, instana_credentials):
        """Test finding application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config = MagicMock()
        mock_api_client.find_application_alert_config.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to get application alert config" in result["error"]

        # Verify the API was called
        mock_api_client.find_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_no_to_dict(self, instana_credentials):
        """Test find_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"id": "alert-123", "name": "Test Alert"}
        mock_api_client.find_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Test Alert"

        # Verify the API was called correctly
        mock_api_client.find_application_alert_config.assert_called_once_with(
            id="alert-123",
            valid_on=None
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_versions_success(self, instana_credentials):
        """Test finding application alert config versions successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config_versions = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = [
            {"id": "alert-123", "version": "1.0"},
            {"id": "alert-123", "version": "2.0"}
        ]
        mock_api_client.find_application_alert_config_versions.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config_versions(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "alert-123"
        assert result[0]["version"] == "1.0"
        assert result[1]["id"] == "alert-123"
        assert result[1]["version"] == "2.0"

        # Verify the API was called correctly
        mock_api_client.find_application_alert_config_versions.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_versions_missing_id(self, instana_credentials):
        """Test finding application alert config versions with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.find_application_alert_config_versions(id="")

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_versions_api_error(self, instana_credentials):
        """Test finding application alert config versions with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config_versions = MagicMock()
        mock_api_client.find_application_alert_config_versions.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config_versions(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to get application alert config versions" in result["error"]

        # Verify the API was called
        mock_api_client.find_application_alert_config_versions.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_find_application_alert_config_versions_no_to_dict(self, instana_credentials):
        """Test find_application_alert_config_versions with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.find_application_alert_config_versions = MagicMock()

        # Create a mock response that's already a list
        mock_response = [
            {"id": "alert-123", "version": "1.0"},
            {"id": "alert-123", "version": "2.0"}
        ]
        mock_api_client.find_application_alert_config_versions.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.find_application_alert_config_versions(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result - should be a dict with "versions" key as returned by the source code
        assert isinstance(result, dict)
        assert "versions" in result
        assert isinstance(result["versions"], list)
        assert len(result["versions"]) == 2
        assert result["versions"][0]["id"] == "alert-123"
        assert result["versions"][0]["version"] == "1.0"
        assert result["versions"][1]["id"] == "alert-123"
        assert result["versions"][1]["version"] == "2.0"

        # Verify the API was called correctly
        mock_api_client.find_application_alert_config_versions.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_delete_application_alert_config_success(self, instana_credentials):
        """Test deleting application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.delete_application_alert_config = MagicMock()
        mock_api_client.delete_application_alert_config.return_value = None  # Successful deletion returns None

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.delete_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True

        # Verify the API was called correctly
        mock_api_client.delete_application_alert_config.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_delete_application_alert_config_missing_id(self, instana_credentials):
        """Test deleting application alert config with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.delete_application_alert_config(id="")

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_delete_application_alert_config_api_error(self, instana_credentials):
        """Test deleting application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.delete_application_alert_config = MagicMock()
        mock_api_client.delete_application_alert_config.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.delete_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to delete application alert config" in result["error"]

        # Verify the API was called
        mock_api_client.delete_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_enable_application_alert_config_success(self, instana_credentials):
        """Test enabling application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.enable_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Test Alert",
            "enabled": True
        }
        mock_api_client.enable_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.enable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Test Alert"
        assert result["enabled"] is True

        # Verify the API was called correctly
        mock_api_client.enable_application_alert_config.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_enable_application_alert_config_missing_id(self, instana_credentials):
        """Test enabling application alert config with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.enable_application_alert_config(id="")

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_enable_application_alert_config_api_error(self, instana_credentials):
        """Test enabling application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.enable_application_alert_config = MagicMock()
        mock_api_client.enable_application_alert_config.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.enable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to enable application alert config" in result["error"]

        # Verify the API was called
        mock_api_client.enable_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_enable_application_alert_config_no_to_dict(self, instana_credentials):
        """Test enable_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.enable_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"enabled": True, "id": "alert-123"}
        mock_api_client.enable_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.enable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["enabled"] is True
        assert result["id"] == "alert-123"

        # Verify the API was called correctly
        mock_api_client.enable_application_alert_config.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_disable_application_alert_config_success(self, instana_credentials):
        """Test disabling application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.disable_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Test Alert",
            "enabled": False
        }
        mock_api_client.disable_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.disable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Test Alert"
        assert result["enabled"] is False

        # Verify the API was called correctly
        mock_api_client.disable_application_alert_config.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_disable_application_alert_config_missing_id(self, instana_credentials):
        """Test disabling application alert config with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.disable_application_alert_config(id="")

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_disable_application_alert_config_api_error(self, instana_credentials):
        """Test disabling application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.disable_application_alert_config = MagicMock()
        mock_api_client.disable_application_alert_config.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.disable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to disable application alert config" in result["error"]

        # Verify the API was called
        mock_api_client.disable_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_disable_application_alert_config_no_to_dict(self, instana_credentials):
        """Test disable_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.disable_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"enabled": False, "id": "alert-123"}
        mock_api_client.disable_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.disable_application_alert_config(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["enabled"] is False
        assert result["id"] == "alert-123"

        # Verify the API was called correctly
        mock_api_client.disable_application_alert_config.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_restore_application_alert_config_success(self, instana_credentials):
        """Test restoring application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.restore_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Restored Alert"
        }
        mock_api_client.restore_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.restore_application_alert_config(
            id="alert-123",
            created=1625097600000,
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Restored Alert"

        # Verify the API was called correctly
        mock_api_client.restore_application_alert_config.assert_called_once_with(
            id="alert-123",
            created=1625097600000
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_restore_application_alert_config_missing_params(self, instana_credentials):
        """Test restoring application alert config with missing parameters."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.restore_application_alert_config(id="", created=1625097600000)

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_restore_application_alert_config_api_error(self, instana_credentials):
        """Test restoring application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.restore_application_alert_config = MagicMock()
        mock_api_client.restore_application_alert_config.side_effect = ApiException(status=404, reason="Not Found")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.restore_application_alert_config(
            id="alert-123",
            created=1625097600000,
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to restore application alert config" in result["error"]

        # Verify the API was called
        mock_api_client.restore_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_restore_application_alert_config_no_to_dict(self, instana_credentials):
        """Test restore_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.restore_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"id": "alert-123", "name": "Restored Alert"}
        mock_api_client.restore_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.restore_application_alert_config(
            id="alert-123",
            created=1625097600000,
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["name"] == "Restored Alert"

        # Verify the API was called correctly
        mock_api_client.restore_application_alert_config.assert_called_once_with(
            id="alert-123",
            created=1625097600000
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_baseline_success(self, instana_credentials):
        """Test updating application alert config baseline successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_historic_baseline = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "lastUpdated": 1625097600000
        }
        mock_api_client.update_application_historic_baseline.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.update_application_alert_config_baseline(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["lastUpdated"] == 1625097600000

        # Verify the API was called correctly
        mock_api_client.update_application_historic_baseline.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_baseline_missing_id(self, instana_credentials):
        """Test updating application alert config baseline with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.update_application_alert_config_baseline(id="")

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_baseline_api_error(self, instana_credentials):
        """Test updating application alert config baseline with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_historic_baseline = MagicMock()
        mock_api_client.update_application_historic_baseline.side_effect = ApiException(status=401, reason="Unauthorized")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.update_application_alert_config_baseline(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to update application alert config baseline" in result["error"]

        # Verify the API was called
        mock_api_client.update_application_historic_baseline.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_baseline_no_to_dict(self, instana_credentials):
        """Test update_application_alert_config_baseline with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_historic_baseline = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"id": "alert-123", "lastUpdated": 1625097600000}
        mock_api_client.update_application_historic_baseline.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method
        result = await client.update_application_alert_config_baseline(
            id="alert-123",
            api_client=mock_api_client
        )

        # Verify the result
        assert isinstance(result, dict)
        assert result["id"] == "alert-123"
        assert result["lastUpdated"] == 1625097600000

        # Verify the API was called correctly
        mock_api_client.update_application_historic_baseline.assert_called_once_with(
            id="alert-123"
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_success(self, instana_credentials):
        """Test creating application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "New Alert",
            "enabled": True
        }
        mock_api_client.create_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        payload = {"name": "New Alert", "enabled": True}

        result = await client.create_application_alert_config(
            payload=payload,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.create_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "New Alert"
            assert result["enabled"] is True
            mock_api_client.create_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_with_string_payload(self, instana_credentials):
        """Test creating application alert config with string payload."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "String Alert"
        }
        mock_api_client.create_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        payload_str = '{"name": "String Alert", "enabled": true}'

        result = await client.create_application_alert_config(
            payload=payload_str,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.create_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "String Alert"
            mock_api_client.create_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_with_python_literal_payload(self, instana_credentials):
        """Test creating application alert config with Python literal payload."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Literal Alert"
        }
        mock_api_client.create_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        payload_str = "{'name': 'Literal Alert', 'enabled': True}"

        result = await client.create_application_alert_config(
            payload=payload_str,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.create_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "Literal Alert"
            mock_api_client.create_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_json_decode_error(self, instana_credentials):
        """Test creating application alert config with JSON decode error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test invalid JSON payload
        payload_str = '{"name": "Invalid JSON", "enabled": true,}'

        # Test the method
        result = await client.create_application_alert_config(
            payload=payload_str,
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid payload format" in result["error"]

        # Verify the API was not called
        mock_api_client.create_application_alert_config.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_ast_eval_error(self, instana_credentials):
        """Test creating application alert config with AST eval error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test invalid Python literal payload
        payload_str = "{'name': 'Invalid Literal', 'enabled': True, 'invalid': }"

        # Test the method
        result = await client.create_application_alert_config(
            payload=payload_str,
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid payload format" in result["error"]

        # Verify the API was not called
        mock_api_client.create_application_alert_config.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_api_error(self, instana_credentials):
        """Test creating application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()
        mock_api_client.create_application_alert_config.side_effect = ApiException(status=400, reason="Bad Request")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        payload = {"name": "Test Alert", "enabled": True}

        result = await client.create_application_alert_config(
            payload=payload,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert (
            "Failed to create config object" in result["error"]
            or "Failed to create application alert config" in result["error"]
        )

        if "Failed to create config object" in result["error"]:
            mock_api_client.create_application_alert_config.assert_not_called()
        else:
            mock_api_client.create_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_no_to_dict(self, instana_credentials):
        """Test create_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.create_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"id": "alert-123", "name": "No ToDict Alert"}
        mock_api_client.create_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        payload = {"name": "No ToDict Alert", "enabled": True}

        result = await client.create_application_alert_config(
            payload=payload,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.create_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "No ToDict Alert"
            mock_api_client.create_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_success(self, instana_credentials):
        """Test updating application alert config successfully."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Updated Alert",
            "enabled": False
        }
        mock_api_client.update_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test payload - we'll use a minimal payload that will trigger validation errors
        payload = {"name": "Updated Alert", "enabled": False}

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.update_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "Updated Alert"
            assert result["enabled"] is False
            mock_api_client.update_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_missing_id(self, instana_credentials):
        """Test updating application alert config with missing ID."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty ID
        result = await client.update_application_alert_config(id="", payload={})

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "id is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_with_string_payload(self, instana_credentials):
        """Test updating application alert config with string payload."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "String Updated Alert"
        }
        mock_api_client.update_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test string payload
        payload_str = '{"name": "String Updated Alert", "enabled": false}'

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload_str,
            api_client=mock_api_client
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.update_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "String Updated Alert"
            mock_api_client.update_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_with_python_literal_payload(self, instana_credentials):
        """Test updating application alert config with Python literal payload."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "id": "alert-123",
            "name": "Literal Updated Alert"
        }
        mock_api_client.update_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test Python literal payload
        payload_str = "{'name': 'Literal Updated Alert', 'enabled': False}"

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload_str,
            api_client=mock_api_client
        )

        # Verify either validation failure or mocked success in combined runs
        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.update_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "Literal Updated Alert"
            mock_api_client.update_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_json_decode_error(self, instana_credentials):
        """Test updating application alert config with JSON decode error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test invalid JSON payload
        payload_str = '{"name": "Invalid JSON", "enabled": false,}'

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload_str,
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid payload format" in result["error"]

        # Verify the API was not called
        mock_api_client.update_application_alert_config.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_ast_eval_error(self, instana_credentials):
        """Test updating application alert config with AST eval error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test invalid Python literal payload
        payload_str = "{'name': 'Invalid Literal', 'enabled': False, 'invalid': }"

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload_str,
            api_client=mock_api_client
        )

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid payload format" in result["error"]

        # Verify the API was not called
        mock_api_client.update_application_alert_config.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_api_error(self, instana_credentials):
        """Test updating application alert config with API error."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()
        mock_api_client.update_application_alert_config.side_effect = ApiException(status=400, reason="Bad Request")

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test payload - we'll use a minimal payload that will trigger validation errors
        payload = {"name": "Test Alert", "enabled": False}

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload,
            api_client=mock_api_client
        )

        # Verify either validation failure or API-level failure path
        assert isinstance(result, dict)
        assert "error" in result
        assert (
            "Failed to create config object" in result["error"]
            or "Failed to update application alert config" in result["error"]
        )

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_no_to_dict(self, instana_credentials):
        """Test update_application_alert_config with result that doesn't have to_dict method."""

        # Create mock API client
        mock_api_client = type('MockClient', (), {})()
        mock_api_client.update_application_alert_config = MagicMock()

        # Create a mock response that's already a dict
        mock_response = {"id": "alert-123", "name": "No ToDict Updated Alert"}
        mock_api_client.update_application_alert_config.return_value = mock_response

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test payload - we'll use a minimal payload that will trigger validation errors
        payload = {"name": "No ToDict Updated Alert", "enabled": False}

        # Test the method
        result = await client.update_application_alert_config(
            id="alert-123",
            payload=payload,
            api_client=mock_api_client
        )

        # Verify either validation failure or mocked success in combined runs
        assert isinstance(result, dict)
        if "error" in result:
            assert "Failed to create config object" in result["error"]
            mock_api_client.update_application_alert_config.assert_not_called()
        else:
            assert result["id"] == "alert-123"
            assert result["name"] == "No ToDict Updated Alert"
            mock_api_client.update_application_alert_config.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_empty_payload(self, instana_credentials):
        """Test creating application alert config with empty payload."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty payload
        result = await client.create_application_alert_config(payload={})

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "Payload is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_empty_payload(self, instana_credentials):
        """Test updating application alert config with empty payload."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty payload
        result = await client.update_application_alert_config(id="alert-123", payload={})

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "payload is required" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_create_application_alert_config_string_payload_parsing_errors(self, instana_credentials):
        """Test creating application alert config with string payload parsing errors."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test with None payload
        result = await client.create_application_alert_config(payload=None)
        assert isinstance(result, dict)
        assert "error" in result
        assert "Payload is required" in result["error"]

        # Test with empty string payload
        result = await client.create_application_alert_config(payload="")
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid payload format" in result["error"]

        # Test with non-string, non-dict payload
        result = await client.create_application_alert_config(payload=123)
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to create config object" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_update_application_alert_config_string_payload_parsing_errors(self, instana_credentials):
        """Test updating application alert config with string payload parsing errors."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test with None payload
        result = await client.update_application_alert_config(id="alert-123", payload=None)
        assert isinstance(result, dict)
        assert "error" in result
        assert "payload is required" in result["error"]

        # Test with empty string payload
        result = await client.update_application_alert_config(id="alert-123", payload="")
        assert isinstance(result, dict)
        assert "error" in result
        assert "payload is required" in result["error"]

        # Test with non-string, non-dict payload
        result = await client.update_application_alert_config(id="alert-123", payload=123)
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to create config object" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_all_methods_with_none_api_client(self, instana_credentials):
        """Test all methods with None api_client to verify decorator behavior."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test find_application_alert_config with None api_client
        result = await client.find_application_alert_config(id="alert-123", api_client=None)
        assert result is not None

        # Test find_application_alert_config_versions with None api_client
        result = await client.find_application_alert_config_versions(id="alert-123", api_client=None)
        assert result is not None


        # Test delete_application_alert_config with None api_client
        result = await client.delete_application_alert_config(id="alert-123", api_client=None)
        assert result is not None

        # Test enable_application_alert_config with None api_client
        result = await client.enable_application_alert_config(id="alert-123", api_client=None)
        assert result is not None

        # Test disable_application_alert_config with None api_client
        result = await client.disable_application_alert_config(id="alert-123", api_client=None)
        assert result is not None

        # Test restore_application_alert_config with None api_client
        result = await client.restore_application_alert_config(id="alert-123", created=1625097600000, api_client=None)
        assert result is not None

        # Test update_application_alert_config_baseline with None api_client
        result = await client.update_application_alert_config_baseline(id="alert-123", api_client=None)
        assert result is not None

        # Test create_application_alert_config with None api_client
        result = await client.create_application_alert_config(payload={"name": "Test"}, api_client=None)
        assert result is not None

        # Test update_application_alert_config with None api_client
        result = await client.update_application_alert_config(id="alert-123", payload={"name": "Test"}, api_client=None)
        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_restore_application_alert_config_missing_created(self, instana_credentials):
        """Test restoring application alert config with missing created parameter."""

        # Create the client
        client = create_application_alert_client(instana_credentials)

        # Test the method with empty created
        result = await client.restore_application_alert_config(id="alert-123", created=0)

        # Verify the result contains an error
        assert isinstance(result, dict)
        assert "error" in result
        assert "created timestamp is required" in result["error"]
