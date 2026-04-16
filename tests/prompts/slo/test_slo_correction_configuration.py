"""Tests for the SLOCorrectionPrompts class."""
import sys
import unittest
from unittest.mock import MagicMock

# Mock fastmcp before importing src.prompts
mock_fastmcp = MagicMock()
# Make the prompt decorator return the original function unchanged
mock_fastmcp.FastMCP.return_value.prompt.return_value = lambda func: func
sys.modules['fastmcp'] = mock_fastmcp

from src.prompts import PROMPT_REGISTRY
from src.prompts.slo.slo_correction_configuration import SLOCorrectionPrompts


class TestSLOCorrectionPrompts(unittest.TestCase):
    """Test cases for the SLOCorrectionPrompts class."""

    def test_get_all_corrections_registered(self):
        """Test that get_all_corrections is registered in the prompt registry."""
        func = SLOCorrectionPrompts.get_all_corrections
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_correction_by_id_registered(self):
        """Test that get_correction_by_id is registered in the prompt registry."""
        func = SLOCorrectionPrompts.get_correction_by_id
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_create_correction_registered(self):
        """Test that create_correction is registered in the prompt registry."""
        func = SLOCorrectionPrompts.create_correction
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_update_correction_registered(self):
        """Test that update_correction is registered in the prompt registry."""
        func = SLOCorrectionPrompts.update_correction
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_delete_correction_registered(self):
        """Test that delete_correction is registered in the prompt registry."""
        func = SLOCorrectionPrompts.delete_correction
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = SLOCorrectionPrompts.get_prompts()
        self.assertEqual(len(prompts), 5)
        self.assertEqual(prompts[0][0], 'get_all_corrections')
        self.assertEqual(prompts[1][0], 'get_correction_by_id')
        self.assertEqual(prompts[2][0], 'create_correction')
        self.assertEqual(prompts[3][0], 'update_correction')
        self.assertEqual(prompts[4][0], 'delete_correction')

    def test_get_all_corrections_prompt_content(self):
        """Test that get_all_corrections returns expected prompt content."""
        result = SLOCorrectionPrompts.get_all_corrections(
            page_size=10,
            page=1,
            query="maintenance",
            slo_id=["slo-123"]
        )
        self.assertIn("Get all SLO correction windows", result)
        self.assertIn("Page size: 10", result)
        self.assertIn("Page: 1", result)
        self.assertIn("Query: maintenance", result)
        self.assertIn("SLO IDs: ['slo-123']", result)

    def test_get_correction_by_id_prompt_content(self):
        """Test that get_correction_by_id returns expected prompt content."""
        result = SLOCorrectionPrompts.get_correction_by_id(id="corr-123")
        self.assertIn("Get SLO correction window", result)
        self.assertIn("ID: corr-123", result)

    def test_create_correction_prompt_content(self):
        """Test that create_correction returns expected prompt content."""
        result = SLOCorrectionPrompts.create_correction(
            name="Maintenance Window",
            scheduling={
                "duration": 2,
                "durationUnit": "hour",
                "startTime": "2026-03-10 14:00:00|IST"
            },
            slo_ids=["slo-123"],
            description="Database upgrade",
            tags=["maintenance"]
        )
        self.assertIn("Create SLO correction window", result)
        self.assertIn("Name: Maintenance Window", result)
        self.assertIn("Description: Database upgrade", result)
        self.assertIn("Tags: ['maintenance']", result)

    def test_update_correction_prompt_content(self):
        """Test that update_correction returns expected prompt content."""
        result = SLOCorrectionPrompts.update_correction(
            id="corr-123",
            name="Updated Maintenance Window",
            scheduling={
                "duration": 3,
                "durationUnit": "hour",
                "startTime": "2026-03-10 15:00:00|IST"
            },
            slo_ids=["slo-123", "slo-456"],
            active=True
        )
        self.assertIn("Update SLO correction window", result)
        self.assertIn("ID: corr-123", result)
        self.assertIn("Name: Updated Maintenance Window", result)
        self.assertIn("Active: True", result)

    def test_delete_correction_prompt_content(self):
        """Test that delete_correction returns expected prompt content."""
        result = SLOCorrectionPrompts.delete_correction(id="corr-123")
        self.assertIn("Delete SLO correction window", result)
        self.assertIn("ID: corr-123", result)


if __name__ == '__main__':
    unittest.main()

