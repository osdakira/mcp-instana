"""Tests for the ActionHistoryPrompts class."""
import sys
import unittest
from unittest.mock import MagicMock

# Mock fastmcp before importing src.prompts
mock_fastmcp = MagicMock()
# Make the prompt decorator return the original function unchanged
mock_fastmcp.FastMCP.return_value.prompt.return_value = lambda func: func
sys.modules['fastmcp'] = mock_fastmcp

from src.prompts import PROMPT_REGISTRY
from src.prompts.automation.action_history import ActionHistoryPrompts


class TestActionHistoryPrompts(unittest.TestCase):
    """Test cases for the ActionHistoryPrompts class."""

    def test_submit_automation_action_registered(self):
        """Test that submit_automation_action is registered in the prompt registry."""
        func = ActionHistoryPrompts.submit_automation_action
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_action_instance_details_registered(self):
        """Test that get_action_instance_details is registered in the prompt registry."""
        func = ActionHistoryPrompts.get_action_instance_details
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_list_action_instances_registered(self):
        """Test that list_action_instances is registered in the prompt registry."""
        func = ActionHistoryPrompts.list_action_instances
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_delete_action_instance_registered(self):
        """Test that delete_action_instance is registered in the prompt registry."""
        func = ActionHistoryPrompts.delete_action_instance
        self.assertTrue(
            any(getattr(item, '__func__', item) == func for item in PROMPT_REGISTRY),
            f"{func} not found in PROMPT_REGISTRY"
        )

    def test_get_prompts_returns_all_prompts(self):
        """Test that get_prompts returns all prompts defined in the class."""
        prompts = ActionHistoryPrompts.get_prompts()
        self.assertEqual(len(prompts), 4)
        self.assertEqual(prompts[0][0], 'submit_automation_action')
        self.assertEqual(prompts[1][0], 'get_action_instance_details')
        self.assertEqual(prompts[2][0], 'list_action_instances')
        self.assertEqual(prompts[3][0], 'delete_action_instance')

    def test_submit_automation_action_prompt_content(self):
        """Test that submit_automation_action returns expected prompt content."""
        payload = {
            "hostId": "host-123",
            "actionId": "action-456",
            "async": "true",
            "timeout": "600"
        }
        result = ActionHistoryPrompts.submit_automation_action(payload=payload)
        self.assertIn("Submit automation action", result)
        self.assertIn(str(payload), result)
        self.assertIn("Required fields", result)
        self.assertIn("actionId", result)
        self.assertIn("hostId", result)

    def test_get_action_instance_details_prompt_content(self):
        """Test that get_action_instance_details returns expected prompt content."""
        result = ActionHistoryPrompts.get_action_instance_details(
            action_instance_id="instance-123",
            window_size=600000,
            to=1234567890000
        )
        self.assertIn("Get action instance details", result)
        self.assertIn("instance-123", result)
        self.assertIn("600000", result)
        self.assertIn("1234567890000", result)

    def test_get_action_instance_details_prompt_content_minimal(self):
        """Test that get_action_instance_details returns expected prompt content with minimal params."""
        result = ActionHistoryPrompts.get_action_instance_details(
            action_instance_id="instance-123"
        )
        self.assertIn("Get action instance details", result)
        self.assertIn("instance-123", result)
        self.assertIn("default", result)
        self.assertIn("current time", result)

    def test_list_action_instances_prompt_content(self):
        """Test that list_action_instances returns expected prompt content."""
        result = ActionHistoryPrompts.list_action_instances(
            window_size=3600000,
            to=1234567890000,
            page=1,
            page_size=50,
            target_snapshot_id="snap-123",
            event_id="event-456",
            search="test",
            types=["script", "webhook"],
            action_statuses=["SUCCESS", "FAILED"],
            order_by="timestamp",
            order_direction="DESC"
        )
        self.assertIn("List action instances", result)
        self.assertIn("3600000", result)
        self.assertIn("1234567890000", result)
        self.assertIn("1", result)
        self.assertIn("50", result)
        self.assertIn("snap-123", result)
        self.assertIn("event-456", result)
        self.assertIn("test", result)
        self.assertIn("script", result)
        self.assertIn("SUCCESS", result)
        self.assertIn("timestamp", result)
        self.assertIn("DESC", result)

    def test_list_action_instances_prompt_content_minimal(self):
        """Test that list_action_instances returns expected prompt content with minimal params."""
        result = ActionHistoryPrompts.list_action_instances()
        self.assertIn("List action instances", result)
        # Should have multiple "None" for optional parameters
        self.assertIn("None", result)

    def test_delete_action_instance_prompt_content(self):
        """Test that delete_action_instance returns expected prompt content."""
        result = ActionHistoryPrompts.delete_action_instance(
            action_instance_id="instance-123",
            from_time=1234567890000,
            to_time=1234567900000
        )
        self.assertIn("Delete action instance", result)
        self.assertIn("instance-123", result)
        self.assertIn("1234567890000", result)
        self.assertIn("1234567900000", result)


    def test_submit_automation_action_with_empty_payload(self):
        """Test submit_automation_action with empty payload"""
        result = ActionHistoryPrompts.submit_automation_action(payload={})
        self.assertIn("Payload: {}", result)
        self.assertIn("Required fields", result)

    def test_submit_automation_action_with_complex_payload(self):
        """Test submit_automation_action with complex payload"""
        payload = {
            "hostId": "host-123",
            "actionId": "action-456",
            "async": "false",
            "timeout": "300",
            "eventId": "event-789",
            "policyId": "policy-012",
            "inputParameters": [{"key": "param1", "value": "value1"}]
        }
        result = ActionHistoryPrompts.submit_automation_action(payload=payload)
        self.assertIn(str(payload), result)

    def test_get_action_instance_details_with_zero_values(self):
        """Test get_action_instance_details with zero values"""
        result = ActionHistoryPrompts.get_action_instance_details(
            action_instance_id="instance-123",
            window_size=0,
            to=0
        )
        # 0 is falsy, so becomes default/current time
        self.assertIn("default", result)
        self.assertIn("current time", result)

    def test_get_action_instance_details_with_special_chars(self):
        """Test get_action_instance_details with special characters in ID"""
        result = ActionHistoryPrompts.get_action_instance_details(
            action_instance_id="instance-123_test.v2"
        )
        self.assertIn("instance-123_test.v2", result)

    def test_list_action_instances_with_empty_lists(self):
        """Test list_action_instances with empty lists"""
        result = ActionHistoryPrompts.list_action_instances(
            types=[],
            action_statuses=[]
        )
        self.assertIn("Types: None", result)
        self.assertIn("Action statuses: None", result)

    def test_list_action_instances_with_event_specification_id(self):
        """Test list_action_instances with event_specification_id"""
        result = ActionHistoryPrompts.list_action_instances(
            event_specification_id="spec-123"
        )
        self.assertIn("Event specification ID: spec-123", result)

    def test_list_action_instances_with_zero_page(self):
        """Test list_action_instances with page=0"""
        result = ActionHistoryPrompts.list_action_instances(page=0)
        # 0 is falsy
        self.assertIn("Page: None", result)

    def test_delete_action_instance_with_special_chars(self):
        """Test delete_action_instance with special characters in ID"""
        result = ActionHistoryPrompts.delete_action_instance(
            action_instance_id="instance-123_test.v2",
            from_time=1234567890000,
            to_time=1234567900000
        )
        self.assertIn("instance-123_test.v2", result)

    def test_all_prompts_return_strings(self):
        """Test that all prompt methods return strings"""
        prompts = ActionHistoryPrompts.get_prompts()
        for name, prompt_func in prompts:
            if name == "submit_automation_action":
                result = prompt_func(payload={})
            elif name == "get_action_instance_details":
                result = prompt_func(action_instance_id="test")
            elif name == "list_action_instances":
                result = prompt_func()
            elif name == "delete_action_instance":
                result = prompt_func(action_instance_id="test", from_time=0, to_time=1)

            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)

    def test_get_prompts_returns_tuples(self):
        """Test that get_prompts returns list of tuples"""
        prompts = ActionHistoryPrompts.get_prompts()
        for item in prompts:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertTrue(callable(item[1]))

    def test_prompt_names_are_unique(self):
        """Test that all prompt names are unique"""
        prompts = ActionHistoryPrompts.get_prompts()
        names = [p[0] for p in prompts]
        self.assertEqual(len(names), len(set(names)))

    def test_class_is_instantiable(self):
        """Test that the class can be instantiated"""
        instance = ActionHistoryPrompts()
        self.assertIsInstance(instance, ActionHistoryPrompts)

    def test_prompts_accessible_from_instance(self):
        """Test that prompts are accessible from instance"""
        instance = ActionHistoryPrompts()
        self.assertTrue(hasattr(instance, 'submit_automation_action'))
        self.assertTrue(hasattr(instance, 'list_action_instances'))

    def test_list_action_instances_with_all_filters(self):
        """Test list_action_instances with all filter parameters"""
        result = ActionHistoryPrompts.list_action_instances(
            window_size=7200000,
            to=1234567890000,
            page=2,
            page_size=100,
            target_snapshot_id="snap-999",
            event_id="event-888",
            event_specification_id="spec-777",
            search="critical",
            types=["script", "webhook", "email"],
            action_statuses=["SUCCESS", "FAILED", "PENDING"],
            order_by="created",
            order_direction="ASC"
        )
        self.assertIn("7200000", result)
        self.assertIn("2", result)
        self.assertIn("100", result)
        self.assertIn("snap-999", result)
        self.assertIn("event-888", result)
        self.assertIn("spec-777", result)
        self.assertIn("critical", result)
        self.assertIn("email", result)
        self.assertIn("PENDING", result)
        self.assertIn("created", result)
        self.assertIn("ASC", result)


if __name__ == '__main__':
    unittest.main()
