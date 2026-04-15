"""Tests for the WebsiteCatalogPrompts class."""
import unittest
from unittest.mock import patch

from src.prompts import PROMPT_REGISTRY
from src.prompts.website.website_catalog import WebsiteCatalogPrompts


class TestWebsiteCatalogPrompts(unittest.TestCase):
    """Test cases for the WebsiteCatalogPrompts class."""

    def test_get_website_catalog_metrics_registered(self):
        """Test that get_website_catalog_metrics is registered in the prompt registry."""
        # The registry contains staticmethod objects, so we need to unwrap them
        func = WebsiteCatalogPrompts.get_website_catalog_metrics
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_catalog_tags_registered(self):
        """Test that get_website_catalog_tags is registered in the prompt registry."""
        func = WebsiteCatalogPrompts.get_website_catalog_tags
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_tag_catalog_registered(self):
        """Test that get_website_tag_catalog is registered in the prompt registry."""
        func = WebsiteCatalogPrompts.get_website_tag_catalog
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = WebsiteCatalogPrompts.get_prompts()
        self.assertEqual(len(prompts), 3)
        self.assertEqual(prompts[0][0], 'get_website_catalog_metrics')
        self.assertEqual(prompts[1][0], 'get_website_catalog_tags')
        self.assertEqual(prompts[2][0], 'get_website_tag_catalog')


if __name__ == '__main__':
    unittest.main()
