"""Tests for the SLOConfigurationPrompts class."""
import sys
import unittest
from unittest.mock import MagicMock

# Mock fastmcp before importing src.prompts
mock_fastmcp = MagicMock()
# Make the prompt decorator return the original function unchanged
mock_fastmcp.FastMCP.return_value.prompt.return_value = lambda func: func
sys.modules['fastmcp'] = mock_fastmcp

from src.prompts import PROMPT_REGISTRY
from src.prompts.slo.slo_configuration import SLOConfigurationPrompts


class TestSLOConfigurationPrompts(unittest.TestCase):
    """Test cases for the SLOConfigurationPrompts class."""

    def test_get_all_slo_configs_registered(self):
        """Test that get_all_slo_configs is registered in the prompt registry."""
        func = SLOConfigurationPrompts.get_all_slo_configs
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_slo_config_by_id_registered(self):
        """Test that get_slo_config_by_id is registered in the prompt registry."""
        func = SLOConfigurationPrompts.get_slo_config_by_id
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_create_slo_config_registered(self):
        """Test that create_slo_config is registered in the prompt registry."""
        func = SLOConfigurationPrompts.create_slo_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_update_slo_config_registered(self):
        """Test that update_slo_config is registered in the prompt registry."""
        func = SLOConfigurationPrompts.update_slo_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_delete_slo_config_registered(self):
        """Test that delete_slo_config is registered in the prompt registry."""
        func = SLOConfigurationPrompts.delete_slo_config
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_all_slo_config_tags_registered(self):
        """Test that get_all_slo_config_tags is registered in the prompt registry."""
        func = SLOConfigurationPrompts.get_all_slo_config_tags
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = SLOConfigurationPrompts.get_prompts()
        self.assertEqual(len(prompts), 6)
        self.assertEqual(prompts[0][0], 'get_all_slo_configs')
        self.assertEqual(prompts[1][0], 'get_slo_config_by_id')
        self.assertEqual(prompts[2][0], 'create_slo_config')
        self.assertEqual(prompts[3][0], 'update_slo_config')
        self.assertEqual(prompts[4][0], 'delete_slo_config')
        self.assertEqual(prompts[5][0], 'get_all_slo_config_tags')

    def test_get_all_slo_configs_prompt_content(self):
        """Test that get_all_slo_configs returns expected prompt content."""
        result = SLOConfigurationPrompts.get_all_slo_configs(
            page_size=10,
            page=1,
            query="test"
        )
        self.assertIn("Get all SLO configurations", result)
        self.assertIn("Page size: 10", result)
        self.assertIn("Page: 1", result)
        self.assertIn("Query: test", result)

    def test_get_slo_config_by_id_prompt_content(self):
        """Test that get_slo_config_by_id returns expected prompt content."""
        result = SLOConfigurationPrompts.get_slo_config_by_id(id="slo-123")
        self.assertIn("Get SLO configuration", result)
        self.assertIn("ID: slo-123", result)

    def test_create_slo_config_prompt_content(self):
        """Test that create_slo_config returns expected prompt content."""
        result = SLOConfigurationPrompts.create_slo_config(
            name="Test SLO",
            entity={"type": "application"},
            indicator={"type": "timeBased"},
            target=0.95,
            time_window={"type": "rolling"},
            tags=["test"]
        )
        self.assertIn("Create SLO configuration", result)
        self.assertIn("Name: Test SLO", result)
        self.assertIn("Target: 0.95", result)

    def test_update_slo_config_prompt_content(self):
        """Test that update_slo_config returns expected prompt content."""
        result = SLOConfigurationPrompts.update_slo_config(
            id="slo-123",
            name="Updated SLO",
            entity={"type": "application"},
            indicator={"type": "timeBased"},
            target=0.99,
            time_window={"type": "rolling"}
        )
        self.assertIn("Update SLO configuration", result)
        self.assertIn("ID: slo-123", result)
        self.assertIn("Name: Updated SLO", result)
        self.assertIn("Target: 0.99", result)

    def test_delete_slo_config_prompt_content(self):
        """Test that delete_slo_config returns expected prompt content."""
        result = SLOConfigurationPrompts.delete_slo_config(id="slo-123")
        self.assertIn("Delete SLO configuration", result)
        self.assertIn("ID: slo-123", result)

    def test_get_all_slo_config_tags_prompt_content(self):
        """Test that get_all_slo_config_tags returns expected prompt content."""
        result = SLOConfigurationPrompts.get_all_slo_config_tags(
            query="prod",
            entity_type="application"
        )
        self.assertIn("Get all SLO configuration tags", result)
        self.assertIn("Query: prod", result)
        self.assertIn("Entity type: application", result)


if __name__ == '__main__':
    unittest.main()

