"""Tests for application settings prompts."""

import unittest

from src.prompts import PROMPT_REGISTRY
from src.prompts.application.application_settings import ApplicationSettingsPrompts


class TestApplicationSettingsPrompts(unittest.TestCase):
    """Unit tests for ApplicationSettingsPrompts."""

    def test_get_prompts_returns_expected_prompt_names_in_order(self):
        prompts = ApplicationSettingsPrompts.get_prompts()

        self.assertEqual(
            [name for name, _ in prompts],
            [
                "get_all_applications_configs",
                "get_application_config",
                "create_application_config",
                "get_all_endpoint_configs",
                "get_endpoint_config",
                "get_all_manual_service_configs",
                "add_manual_service_config",
                "get_service_config",
            ],
        )

    def test_get_prompts_returns_callable_prompt_objects(self):
        prompts = ApplicationSettingsPrompts.get_prompts()

        self.assertEqual(len(prompts), 8)
        for name, prompt in prompts:
            self.assertIsInstance(name, str)
            self.assertTrue(callable(prompt))

    def test_get_prompts_is_consistent_between_class_and_instance(self):
        class_prompts = ApplicationSettingsPrompts.get_prompts()
        instance_prompts = ApplicationSettingsPrompts().get_prompts()

        self.assertEqual(class_prompts, instance_prompts)

    def test_all_prompts_are_registered_in_prompt_registry(self):
        raw_class_dict = ApplicationSettingsPrompts.__dict__

        for name, _ in ApplicationSettingsPrompts.get_prompts():
            self.assertIn(raw_class_dict[name], PROMPT_REGISTRY)

    def test_prompt_registry_contains_staticmethod_wrappers_for_each_prompt(self):
        raw_class_dict = ApplicationSettingsPrompts.__dict__

        expected_names = [name for name, _ in ApplicationSettingsPrompts.get_prompts()]
        for name in expected_names:
            self.assertIn(name, raw_class_dict)
            self.assertIn(raw_class_dict[name], PROMPT_REGISTRY)
            self.assertIsInstance(raw_class_dict[name], staticmethod)

    def test_class_is_stateless_and_instantiable(self):
        instance = ApplicationSettingsPrompts()

        self.assertIsInstance(instance, ApplicationSettingsPrompts)
        self.assertEqual(vars(instance), {})

    def test_get_all_applications_configs_returns_expected_string(self):
        result = ApplicationSettingsPrompts.get_all_applications_configs()

        self.assertEqual(result, "Retrieve all application configurations")

    def test_get_application_config_includes_id(self):
        result = ApplicationSettingsPrompts.get_application_config("app-123")

        self.assertEqual(result, "Retrieve application configuration with ID: app-123")

    def test_get_application_config_accepts_empty_and_special_character_ids(self):
        empty_result = ApplicationSettingsPrompts.get_application_config("")
        special_result = ApplicationSettingsPrompts.get_application_config("app-123-test_config.v2")

        self.assertEqual(empty_result, "Retrieve application configuration with ID: ")
        self.assertIn("app-123-test_config.v2", special_result)

    def test_create_application_config_with_required_label_only(self):
        result = ApplicationSettingsPrompts.create_application_config("My App")

        self.assertEqual(
            result,
            "Create application perspective configuration with label: My App",
        )

    def test_create_application_config_includes_all_optional_fields_when_truthy(self):
        result = ApplicationSettingsPrompts.create_application_config(
            label="My App",
            scope="INCLUDE_NO_DOWNSTREAM",
            boundary_scope="INBOUND",
            access_rules="CUSTOM",
            tag_filter_expression={"type": "TAG_FILTER", "name": "service.name"},
        )

        self.assertIn("label: My App", result)
        self.assertIn("scope: INCLUDE_NO_DOWNSTREAM", result)
        self.assertIn("boundaryScope: INBOUND", result)
        self.assertIn("accessRules: CUSTOM", result)
        self.assertIn(
            "tagFilterExpression: {'type': 'TAG_FILTER', 'name': 'service.name'}",
            result,
        )

    def test_create_application_config_omits_falsy_optional_fields(self):
        result = ApplicationSettingsPrompts.create_application_config(
            label="Test App",
            scope="",
            boundary_scope=None,
            access_rules=None,
            tag_filter_expression={},
        )

        self.assertEqual(
            result,
            "Create application perspective configuration with label: Test App",
        )
        self.assertNotIn("scope:", result)
        self.assertNotIn("boundaryScope:", result)
        self.assertNotIn("accessRules:", result)
        self.assertNotIn("tagFilterExpression:", result)

    def test_create_application_config_handles_complex_tag_filter(self):
        complex_filter = {
            "type": "EXPRESSION",
            "logicalOperator": "AND",
            "elements": [
                {
                    "type": "TAG_FILTER",
                    "name": "service.name",
                    "operator": "EQUALS",
                    "value": "my-service",
                },
                {
                    "type": "TAG_FILTER",
                    "name": "environment",
                    "operator": "CONTAINS",
                    "value": "prod",
                },
            ],
        }

        result = ApplicationSettingsPrompts.create_application_config(
            label="Test App",
            tag_filter_expression=complex_filter,
        )

        self.assertIn("tagFilterExpression:", result)
        self.assertIn("'logicalOperator': 'AND'", result)
        self.assertIn("'name': 'environment'", result)

    def test_create_application_config_supports_multiple_scope_values(self):
        scopes = [
            "INCLUDE_ALL_DOWNSTREAM",
            "INCLUDE_IMMEDIATE_DOWNSTREAM_DATABASE_AND_MESSAGING",
            "INCLUDE_NO_DOWNSTREAM",
        ]

        for scope in scopes:
            result = ApplicationSettingsPrompts.create_application_config(
                label="Test App",
                scope=scope,
            )
            self.assertIn(f"scope: {scope}", result)

    def test_create_application_config_supports_multiple_boundary_scope_values(self):
        boundary_scopes = ["ALL", "INBOUND", "DEFAULT"]

        for boundary_scope in boundary_scopes:
            result = ApplicationSettingsPrompts.create_application_config(
                label="Test App",
                boundary_scope=boundary_scope,
            )
            self.assertIn(f"boundaryScope: {boundary_scope}", result)

    def test_create_application_config_supports_multiple_access_rule_values(self):
        access_rules = ["READ_WRITE_GLOBAL", "READ_ONLY_GLOBAL", "CUSTOM"]

        for access_rule in access_rules:
            result = ApplicationSettingsPrompts.create_application_config(
                label="Test App",
                access_rules=access_rule,
            )
            self.assertIn(f"accessRules: {access_rule}", result)

    def test_create_application_config_docstring_contains_key_sections(self):
        docstring = ApplicationSettingsPrompts.create_application_config.__doc__

        self.assertIsInstance(docstring, str)
        assert docstring is not None
        self.assertIn("Create a new Application Perspective configuration", docstring)
        self.assertIn("REQUIRED:", docstring)
        self.assertIn("OPTIONAL", docstring)
        self.assertIn("ELICITATION QUESTIONS", docstring)
        self.assertIn("Example with all options", docstring)

    def test_get_all_endpoint_configs_returns_expected_string(self):
        result = ApplicationSettingsPrompts.get_all_endpoint_configs()

        self.assertEqual(result, "Retrieve all endpoint configurations")

    def test_get_endpoint_config_includes_id(self):
        result = ApplicationSettingsPrompts.get_endpoint_config("endpoint-123")

        self.assertEqual(result, "Get endpoint configuration with ID: endpoint-123")

    def test_get_endpoint_config_accepts_special_character_ids(self):
        result = ApplicationSettingsPrompts.get_endpoint_config("endpoint-123-test_config.v2")

        self.assertIn("endpoint-123-test_config.v2", result)

    def test_get_all_manual_service_configs_returns_expected_string(self):
        result = ApplicationSettingsPrompts.get_all_manual_service_configs()

        self.assertEqual(result, "Retrieve all manual service configurations")

    def test_add_manual_service_config_with_required_fields(self):
        result = ApplicationSettingsPrompts.add_manual_service_config(
            enabled=True,
            tag_filter_expression={"type": "TAG_FILTER"},
        )

        self.assertIn("Tag filter: {'type': 'TAG_FILTER'}", result)
        self.assertIn("Unmonitored service name: None", result)
        self.assertIn("Existing service ID: None", result)
        self.assertIn("Description: None", result)
        self.assertIn("Enabled: True", result)

    def test_add_manual_service_config_includes_all_optional_fields(self):
        result = ApplicationSettingsPrompts.add_manual_service_config(
            enabled=True,
            tag_filter_expression={"type": "TAG_FILTER"},
            unmonitored_service_name="test-service",
            existing_service_id="service-123",
            description="Test description",
        )

        self.assertIn("test-service", result)
        self.assertIn("service-123", result)
        self.assertIn("Test description", result)

    def test_add_manual_service_config_false_enabled_renders_true_due_to_current_behavior(self):
        result = ApplicationSettingsPrompts.add_manual_service_config(
            enabled=False,
            tag_filter_expression={"type": "TAG_FILTER"},
        )

        self.assertIn("Enabled: True", result)

    def test_add_manual_service_config_empty_optional_strings_render_none(self):
        result = ApplicationSettingsPrompts.add_manual_service_config(
            enabled=True,
            tag_filter_expression={},
            unmonitored_service_name="",
            existing_service_id="",
            description="",
        )

        self.assertIn("Unmonitored service name: None", result)
        self.assertIn("Existing service ID: None", result)
        self.assertIn("Description: None", result)

    def test_add_manual_service_config_handles_complex_tag_filter(self):
        complex_filter = {
            "type": "EXPRESSION",
            "logicalOperator": "OR",
            "elements": [
                {
                    "type": "TAG_FILTER",
                    "name": "call.http.status",
                    "operator": "GREATER_THAN",
                    "value": "400",
                }
            ],
        }

        result = ApplicationSettingsPrompts.add_manual_service_config(
            enabled=True,
            tag_filter_expression=complex_filter,
            unmonitored_service_name="external-api",
            description="External API service",
        )

        self.assertIn("external-api", result)
        self.assertIn("External API service", result)
        self.assertIn("'logicalOperator': 'OR'", result)

    def test_add_manual_service_config_docstring_exists(self):
        self.assertEqual(
            ApplicationSettingsPrompts.add_manual_service_config.__doc__,
            "Create a manual service mapping configuration",
        )

    def test_get_service_config_includes_id(self):
        result = ApplicationSettingsPrompts.get_service_config("service-config-123")

        self.assertEqual(result, "Get service configuration with ID: service-config-123")

    def test_get_service_config_accepts_special_character_ids(self):
        result = ApplicationSettingsPrompts.get_service_config("service-123-test_config.v2")

        self.assertIn("service-123-test_config.v2", result)


if __name__ == "__main__":
    unittest.main()

