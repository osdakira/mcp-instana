"""Tests for the WebsiteConfigurationPrompts class."""
import unittest
from unittest.mock import patch

from src.prompts import PROMPT_REGISTRY
from src.prompts.website.website_configuration import WebsiteConfigurationPrompts


class TestWebsiteConfigurationPrompts(unittest.TestCase):
    """Test cases for the WebsiteConfigurationPrompts class."""

    def test_get_websites_registered(self):
        """Test that get_websites is registered in the prompt registry."""
        # The registry contains staticmethod objects, so we need to unwrap them
        func = WebsiteConfigurationPrompts.get_websites
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_registered(self):
        """Test that get_website is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.get_website
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_create_website_registered(self):
        """Test that create_website is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.create_website
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_delete_website_registered(self):
        """Test that delete_website is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.delete_website
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_rename_website_registered(self):
        """Test that rename_website is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.rename_website
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_geo_location_configuration_registered(self):
        """Test that get_website_geo_location_configuration is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.get_website_geo_location_configuration
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_update_website_geo_location_configuration_registered(self):
        """Test that update_website_geo_location_configuration is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.update_website_geo_location_configuration
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_website_ip_masking_configuration_registered(self):
        """Test that get_website_ip_masking_configuration is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.get_website_ip_masking_configuration
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_update_website_ip_masking_configuration_registered(self):
        """Test that update_website_ip_masking_configuration is registered in the prompt registry."""
        func = WebsiteConfigurationPrompts.update_website_ip_masking_configuration
        self.assertTrue(any(
            getattr(item, '__func__', item) == func
            for item in PROMPT_REGISTRY
        ))

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = WebsiteConfigurationPrompts.get_prompts()
        self.assertEqual(len(prompts), 9)
        self.assertEqual(prompts[0][0], 'get_websites')
        self.assertEqual(prompts[1][0], 'get_website')
        self.assertEqual(prompts[2][0], 'create_website')
        self.assertEqual(prompts[3][0], 'delete_website')
        self.assertEqual(prompts[4][0], 'rename_website')
        self.assertEqual(prompts[5][0], 'get_website_geo_location_configuration')
        self.assertEqual(prompts[6][0], 'update_website_geo_location_configuration')
        self.assertEqual(prompts[7][0], 'get_website_ip_masking_configuration')
        self.assertEqual(prompts[8][0], 'update_website_ip_masking_configuration')

    def test_get_websites_prompt_content(self):
        """Test that get_websites returns expected prompt content."""
        result = WebsiteConfigurationPrompts.get_websites()
        self.assertIn("Get all websites", result)
        self.assertIn("configured website monitoring", result)

    def test_get_website_prompt_content(self):
        """Test that get_website returns expected prompt content."""
        result = WebsiteConfigurationPrompts.get_website(website_id="web-123")
        self.assertIn("Get website configuration", result)
        self.assertIn("web-123", result)

    def test_create_website_prompt_content(self):
        """Test that create_website returns expected prompt content."""
        payload = {"name": "Test Website"}
        result = WebsiteConfigurationPrompts.create_website(payload=payload)
        self.assertIn("Create website", result)
        self.assertIn(str(payload), result)

    def test_delete_website_prompt_content(self):
        """Test that delete_website returns expected prompt content."""
        result = WebsiteConfigurationPrompts.delete_website(website_id="web-123")
        self.assertIn("Delete website", result)
        self.assertIn("web-123", result)

    def test_rename_website_prompt_content(self):
        """Test that rename_website returns expected prompt content."""
        payload = {"name": "New Name"}
        result = WebsiteConfigurationPrompts.rename_website(website_id="web-123", payload=payload)
        self.assertIn("Rename website", result)
        self.assertIn("web-123", result)
        self.assertIn(str(payload), result)

    def test_get_website_geo_location_configuration_prompt_content(self):
        """Test that get_website_geo_location_configuration returns expected prompt content."""
        result = WebsiteConfigurationPrompts.get_website_geo_location_configuration(website_id="web-123")
        self.assertIn("geo-location configuration", result)
        self.assertIn("web-123", result)

    def test_update_website_geo_location_configuration_prompt_content(self):
        """Test that update_website_geo_location_configuration returns expected prompt content."""
        payload = {"enabled": True}
        result = WebsiteConfigurationPrompts.update_website_geo_location_configuration(
            website_id="web-123", payload=payload
        )
        self.assertIn("Update website geo-location", result)
        self.assertIn("web-123", result)
        self.assertIn(str(payload), result)

    def test_get_website_ip_masking_configuration_prompt_content(self):
        """Test that get_website_ip_masking_configuration returns expected prompt content."""
        result = WebsiteConfigurationPrompts.get_website_ip_masking_configuration(website_id="web-123")
        self.assertIn("IP masking configuration", result)
        self.assertIn("web-123", result)

    def test_update_website_ip_masking_configuration_prompt_content(self):
        """Test that update_website_ip_masking_configuration returns expected prompt content."""
        payload = {"enabled": False}
        result = WebsiteConfigurationPrompts.update_website_ip_masking_configuration(
            website_id="web-123", payload=payload
        )
        self.assertIn("Update website IP masking", result)
        self.assertIn("web-123", result)
        self.assertIn(str(payload), result)

    def test_all_prompts_return_strings(self):
        """Test that all prompt methods return strings."""
        prompts = WebsiteConfigurationPrompts.get_prompts()
        for name, prompt_func in prompts:
            if name == "get_websites":
                result = prompt_func()
            elif name == "get_website":
                result = prompt_func(website_id="test")
            elif name == "create_website":
                result = prompt_func(payload={})
            elif name == "delete_website":
                result = prompt_func(website_id="test")
            elif name == "rename_website":
                result = prompt_func(website_id="test", payload={})
            elif name == "get_website_geo_location_configuration":
                result = prompt_func(website_id="test")
            elif name == "update_website_geo_location_configuration":
                result = prompt_func(website_id="test", payload={})
            elif name == "get_website_ip_masking_configuration":
                result = prompt_func(website_id="test")
            elif name == "update_website_ip_masking_configuration":
                result = prompt_func(website_id="test", payload={})

            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)

    def test_class_is_instantiable(self):
        """Test that the class can be instantiated."""
        instance = WebsiteConfigurationPrompts()
        self.assertIsInstance(instance, WebsiteConfigurationPrompts)


if __name__ == '__main__':
    unittest.main()
