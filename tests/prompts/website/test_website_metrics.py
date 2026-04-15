"""Tests for the WebsiteMetricsPrompts class."""
import unittest
from unittest.mock import patch

from src.prompts import PROMPT_REGISTRY
from src.prompts.website.website_metrics import WebsiteMetricsPrompts


class TestWebsiteMetricsPrompts(unittest.TestCase):
    """Test cases for the WebsiteMetricsPrompts class."""

    def test_get_website_beacon_metrics_v2_registered(self):
        """Test that get_website_beacon_metrics_v2 is registered in the prompt registry."""
        # The registry contains staticmethod objects, so we need to unwrap them
        func = WebsiteMetricsPrompts.get_website_beacon_metrics_v2
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_page_load_registered(self):
        """Test that get_website_page_load is registered in the prompt registry."""
        func = WebsiteMetricsPrompts.get_website_page_load
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = WebsiteMetricsPrompts.get_prompts()
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0][0], 'get_website_beacon_metrics_v2')
        self.assertEqual(prompts[1][0], 'get_website_page_load')


if __name__ == '__main__':
    unittest.main()
