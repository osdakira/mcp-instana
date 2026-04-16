import json
from types import SimpleNamespace

from mcp.types import EmbeddedResource, TextContent, TextResourceContents

from src.infrastructure.elicitation_handler import ElicitationHandler


class StubRegistry:
    def __init__(self, capability=None):
        self._capability = capability

    def resolve(self, entity_class, entity_kind):
        return self._capability


def make_intent(entity_class="jvm", entity_kind="application", metric_category="cpu"):
    return SimpleNamespace(
        entity_class=entity_class,
        entity_kind=entity_kind,
        metric_category=metric_category,
    )


def make_capability(
    entity_type="jvmRuntimePlatform",
    metrics=None,
    tag_filters=None,
    aggregations=None,
):
    return SimpleNamespace(
        entity_type=entity_type,
        metrics=metrics or [],
        tag_filters=tag_filters or [],
        aggregations=aggregations or [],
    )


class TestElicitationHandlerCheckAmbiguity:
    def test_check_ambiguity_unknown_entity(self):
        handler = ElicitationHandler()
        intent = make_intent(entity_class="unknown", metric_category="cpu")

        result = handler.check_ambiguity(intent, StubRegistry(), resolved_metrics=None)

        assert result is not None
        assert result.type == "clarification"
        assert "don't recognize the entity" in result.message
        assert len(result.options) == 7
        assert result.context["normalized_intent"] == intent

    def test_check_ambiguity_unknown_metric_with_capability(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="unknown")
        capability = make_capability(
            entity_type="jvmRuntimePlatform",
            metrics=[f"metric.{i}" for i in range(12)],
        )

        result = handler.check_ambiguity(
            intent,
            StubRegistry(capability),
            resolved_metrics=None,
        )

        assert result is not None
        assert result.type == "choice"
        assert "don't recognize the metric" in result.message
        assert "jvmRuntimePlatform" in result.message
        assert len(result.options) == 10
        assert result.options[0] == {"label": "metric.0", "value": "metric.0"}
        assert result.context["entity_type"] == "jvmRuntimePlatform"

    def test_check_ambiguity_unknown_metric_without_capability(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="unknown")

        result = handler.check_ambiguity(
            intent,
            StubRegistry(None),
            resolved_metrics=None,
        )

        assert result is not None
        assert result.type == "clarification"
        assert "Please provide a valid metric name" in result.message
        assert result.options == []

    def test_check_ambiguity_multiple_metric_matches(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="cpu")

        result = handler.check_ambiguity(
            intent,
            StubRegistry(),
            resolved_metrics=["cpu.used", "cpu.limit"],
        )

        assert result is not None
        assert result.type == "choice"
        assert "Multiple metrics match 'cpu'" in result.message
        assert result.options == [
            {"label": "cpu.used", "value": "cpu.used"},
            {"label": "cpu.limit", "value": "cpu.limit"},
        ]
        assert result.context["resolved_metrics"] == ["cpu.used", "cpu.limit"]

    def test_check_ambiguity_no_metric_found_with_capability(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="threads")
        capability = make_capability(
            entity_type="jvmRuntimePlatform",
            metrics=[f"metric.{i}" for i in range(25)],
        )

        result = handler.check_ambiguity(
            intent,
            StubRegistry(capability),
            resolved_metrics=[],
        )

        assert result is not None
        assert result.type == "choice"
        assert "No metrics found matching 'threads'" in result.message
        assert "jvmRuntimePlatform" in result.message
        assert len(result.options) == 20
        assert result.options[-1] == {"label": "metric.19", "value": "metric.19"}

    def test_check_ambiguity_no_metric_found_without_capability(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="threads")

        result = handler.check_ambiguity(
            intent,
            StubRegistry(None),
            resolved_metrics=[],
        )

        assert result is not None
        assert result.type == "clarification"
        assert "Could not find metrics for 'threads'" in result.message
        assert result.options == []

    def test_check_ambiguity_returns_none_when_not_ambiguous(self):
        handler = ElicitationHandler()
        intent = make_intent(entity_class="jvm", metric_category="cpu")

        result = handler.check_ambiguity(
            intent,
            StubRegistry(),
            resolved_metrics=["cpu.used"],
        )

        assert result is None


class TestElicitationHandlerHelpers:
    def test_create_unknown_entity_elicitation(self):
        handler = ElicitationHandler()
        intent = make_intent(entity_class="mystery-box")

        result = handler._create_unknown_entity_elicitation(intent)

        assert result.type == "clarification"
        assert "mystery-box" in result.message
        assert result.options[0] == {"label": "Kubernetes Pod", "value": "kubernetes pod"}
        assert result.options[-1] == {"label": "GenAI/LLM", "value": "genai llm"}

    def test_create_multiple_metrics_elicitation(self):
        handler = ElicitationHandler()
        intent = make_intent(metric_category="memory")

        result = handler._create_multiple_metrics_elicitation(
            intent,
            ["memory.used", "memory.limit"],
        )

        assert result.type == "choice"
        assert "Multiple metrics match 'memory'" in result.message
        assert result.options == [
            {"label": "memory.used", "value": "memory.used"},
            {"label": "memory.limit", "value": "memory.limit"},
        ]


class TestCreateSchemaElicitation:
    def test_create_schema_elicitation_with_full_schema(self):
        handler = ElicitationHandler()
        schema = {
            "type": "jvmRuntimePlatform",
            "parameters": {
                "metrics": {
                    "metric": ["jvm.heap.used", "jvm.heap.maxSize"],
                    "aggregation": {"enum": ["mean", "max", "min"]},
                },
                "tagFilterElements": {
                    "enum": ["host.name", "jvm.name"],
                },
            },
        }

        result = handler.create_schema_elicitation(
            entity_type="jvmRuntimePlatform",
            schema=schema,
            intent="show heap usage by host",
        )

        assert isinstance(result, list)
        assert len(result) == 2

        text_part = result[0]
        resource_part = result[1]

        assert isinstance(text_part, TextContent)
        assert "show heap usage by host" in text_part.text
        assert "2 available metrics" in text_part.text
        assert "2 available tag filters" in text_part.text
        assert "Aggregations: mean, max, min" in text_part.text
        assert '"selectedMetrics"' in text_part.text
        assert '"groupBy"' in text_part.text

        assert isinstance(resource_part, EmbeddedResource)
        assert isinstance(resource_part.resource, TextResourceContents)
        assert str(resource_part.resource.uri) == "schema://jvmRuntimePlatform"
        assert resource_part.resource.mimeType == "application/json"

        embedded_schema = json.loads(resource_part.resource.text)
        assert embedded_schema == schema

    def test_create_schema_elicitation_with_missing_optional_sections(self):
        handler = ElicitationHandler()
        schema = {
            "type": "host",
            "parameters": {
                "metrics": {}
            },
        }

        result = handler.create_schema_elicitation(
            entity_type="host",
            schema=schema,
            intent="show cpu",
        )

        assert len(result) == 2
        assert isinstance(result[0], TextContent)
        assert "0 available metrics" in result[0].text
        assert "0 available tag filters" in result[0].text
        assert "Aggregations: N/A" in result[0].text

        assert isinstance(result[1], EmbeddedResource)
        assert json.loads(result[1].resource.text) == schema

    def test_create_schema_elicitation_with_non_dict_tag_filter_elements(self):
        handler = ElicitationHandler()
        schema = {
            "type": "host",
            "parameters": {
                "metrics": {
                    "metric": ["cpu.used"],
                    "aggregation": {"enum": []},
                },
                "tagFilterElements": ["unexpected", "shape"],
            },
        }

        result = handler.create_schema_elicitation(
            entity_type="host",
            schema=schema,
            intent="show cpu",
        )

        assert len(result) == 2
        assert "1 available metrics" in result[0].text
        assert "0 available tag filters" in result[0].text
        assert "Aggregations: N/A" in result[0].text

# Made with Bob
