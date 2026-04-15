"""Tests for the SLOReportPrompts class."""
import sys
import unittest
from unittest.mock import MagicMock

# Mock fastmcp before importing src.prompts
mock_fastmcp = MagicMock()
# Make the prompt decorator return the original function unchanged
mock_fastmcp.FastMCP.return_value.prompt.return_value = lambda func: func
sys.modules['fastmcp'] = mock_fastmcp

from src.prompts import PROMPT_REGISTRY
from src.prompts.slo.slo_report import SLOReportPrompts


class TestSLOReportPrompts(unittest.TestCase):
    """Test cases for the SLOReportPrompts class."""

    def test_get_slo_report_registered(self):
        """Test that get_slo_report is registered in the prompt registry."""
        func = SLOReportPrompts.get_slo_report
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = SLOReportPrompts.get_prompts()
        self.assertEqual(len(prompts), 1)
        self.assertEqual(prompts[0][0], 'get_slo_report')

    def test_get_slo_report_prompt_content(self):
        """Test that get_slo_report returns expected prompt content."""
        result = SLOReportPrompts.get_slo_report(
            slo_id="slo-123",
            var_from="1234567890000",
            to="1234567899999"
        )
        self.assertIn("Get SLO report", result)
        self.assertIn("SLO ID: slo-123", result)
        self.assertIn("From: 1234567890000", result)
        self.assertIn("To: 1234567899999", result)

    def test_get_slo_report_with_corrections(self):
        """Test that get_slo_report handles correction IDs."""
        result = SLOReportPrompts.get_slo_report(
            slo_id="slo-123",
            exclude_correction_id=["corr-1"],
            include_correction_id=["corr-2"]
        )
        self.assertIn("Get SLO report", result)
        self.assertIn("SLO ID: slo-123", result)
        self.assertIn("Exclude correction IDs: ['corr-1']", result)
        self.assertIn("Include correction IDs: ['corr-2']", result)


if __name__ == '__main__':
    unittest.main()

