"""Tests for the WebsiteAnalyzePrompts class."""
import unittest
from unittest.mock import patch

from src.prompts import PROMPT_REGISTRY
from src.prompts.website.website_analyze import WebsiteAnalyzePrompts


class TestWebsiteAnalyzePrompts(unittest.TestCase):
    """Test cases for the WebsiteAnalyzePrompts class."""

    def test_get_website_beacon_groups_registered(self):
        """Test that get_website_beacon_groups is registered in the prompt registry."""
        # The registry contains staticmethod objects, so we need to unwrap them
        func = WebsiteAnalyzePrompts.get_website_beacon_groups
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_beacons_registered(self):
        """Test that get_website_beacons is registered in the prompt registry."""
        func = WebsiteAnalyzePrompts.get_website_beacons
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = WebsiteAnalyzePrompts.get_prompts()
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0][0], 'get_website_beacon_groups')
        self.assertEqual(prompts[1][0], 'get_website_beacons')


if __name__ == '__main__':
    unittest.main()
