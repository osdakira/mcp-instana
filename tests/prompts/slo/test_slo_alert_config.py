"""Tests for the SLOAlertConfigPrompts class."""
import sys
import unittest
from unittest.mock import MagicMock

# Mock fastmcp before importing src.prompts
mock_fastmcp = MagicMock()
# Make the prompt decorator return the original function unchanged
mock_fastmcp.FastMCP.return_value.prompt.return_value = lambda func: func
sys.modules['fastmcp'] = mock_fastmcp

from src.prompts import PROMPT_REGISTRY
from src.prompts.slo.slo_alert_config import SLOAlertConfigPrompts


class TestSLOAlertConfigPrompts(unittest.TestCase):
    """Test cases for the SLOAlertConfigPrompts class."""

    def test_find_active_alert_configs_registered(self):
        """Test that find_active_alert_configs is registered in the prompt registry."""
        # Check if the function is in the registry (may be wrapped in staticmethod)
        func = SLOAlertConfigPrompts.find_active_alert_configs
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_find_alert_config_registered(self):
        """Test that find_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.find_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_find_alert_config_versions_registered(self):
        """Test that find_alert_config_versions is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.find_alert_config_versions
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_create_alert_config_registered(self):
        """Test that create_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.create_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_update_alert_config_registered(self):
        """Test that update_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.update_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_delete_alert_config_registered(self):
        """Test that delete_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.delete_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_disable_alert_config_registered(self):
        """Test that disable_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.disable_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_enable_alert_config_registered(self):
        """Test that enable_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.enable_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_restore_alert_config_registered(self):
        """Test that restore_alert_config is registered in the prompt registry."""
        func = SLOAlertConfigPrompts.restore_alert_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = SLOAlertConfigPrompts.get_prompts()
        self.assertEqual(len(prompts), 9)
        self.assertEqual(prompts[0][0], 'find_active_alert_configs')
        self.assertEqual(prompts[1][0], 'find_alert_config')
        self.assertEqual(prompts[2][0], 'find_alert_config_versions')
        self.assertEqual(prompts[3][0], 'create_alert_config')
        self.assertEqual(prompts[4][0], 'update_alert_config')
        self.assertEqual(prompts[5][0], 'delete_alert_config')
        self.assertEqual(prompts[6][0], 'disable_alert_config')
        self.assertEqual(prompts[7][0], 'enable_alert_config')
        self.assertEqual(prompts[8][0], 'restore_alert_config')

    def test_find_active_alert_configs_prompt_content(self):
        """Test that find_active_alert_configs returns expected prompt content."""
        result = SLOAlertConfigPrompts.find_active_alert_configs(
            slo_id="slo-123",
            alert_ids=["alert-1", "alert-2"]
        )
        self.assertIn("Find active SLO alert configurations", result)
        self.assertIn("SLO ID: slo-123", result)
        self.assertIn("Alert IDs: ['alert-1', 'alert-2']", result)

    def test_find_alert_config_prompt_content(self):
        """Test that find_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.find_alert_config(
            id="alert-123",
            valid_on=1234567890000
        )
        self.assertIn("Find SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)
        self.assertIn("Valid on: 1234567890000", result)

    def test_find_alert_config_versions_prompt_content(self):
        """Test that find_alert_config_versions returns expected prompt content."""
        result = SLOAlertConfigPrompts.find_alert_config_versions(id="alert-123")
        self.assertIn("Find SLO alert configuration versions", result)
        self.assertIn("ID: alert-123", result)

    def test_create_alert_config_prompt_content(self):
        """Test that create_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.create_alert_config(
            name="Test Alert",
            description="Test alert description",
            slo_ids=["slo-123"],
            rule={"alertType": "ERROR_BUDGET"},
            severity=10,
            alert_channel_ids=["channel-1"],
            time_threshold={"expiry": 604800000}
        )
        self.assertIn("Create SLO alert configuration", result)
        self.assertIn("Name: Test Alert", result)
        self.assertIn("Description: Test alert description", result)
        self.assertIn("Severity: 10", result)

    def test_update_alert_config_prompt_content(self):
        """Test that update_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.update_alert_config(
            id="alert-123",
            name="Updated Alert",
            description="Updated description",
            slo_ids=["slo-123"],
            rule={"alertType": "ERROR_BUDGET"},
            severity=5,
            alert_channel_ids=["channel-1"],
            time_threshold={"expiry": 604800000}
        )
        self.assertIn("Update SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)
        self.assertIn("Name: Updated Alert", result)
        self.assertIn("Severity: 5", result)

    def test_delete_alert_config_prompt_content(self):
        """Test that delete_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.delete_alert_config(id="alert-123")
        self.assertIn("Delete SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)

    def test_disable_alert_config_prompt_content(self):
        """Test that disable_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.disable_alert_config(id="alert-123")
        self.assertIn("Disable SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)

    def test_enable_alert_config_prompt_content(self):
        """Test that enable_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.enable_alert_config(id="alert-123")
        self.assertIn("Enable SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)

    def test_restore_alert_config_prompt_content(self):
        """Test that restore_alert_config returns expected prompt content."""
        result = SLOAlertConfigPrompts.restore_alert_config(
            id="alert-123",
            created=1234567890000
        )
        self.assertIn("Restore SLO alert configuration", result)
        self.assertIn("ID: alert-123", result)
        self.assertIn("Created timestamp: 1234567890000", result)


if __name__ == '__main__':
    unittest.main()

