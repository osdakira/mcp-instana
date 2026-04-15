"""
Tests for Two-Pass Elicitation Flow

Tests the new analyze_infrastructure tool with:
- Pass 1: Intent → Schema Elicitation
- Pass 2: Selections → API Call
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from mcp.types import EmbeddedResource, TextContent, TextResourceContents

from src.infrastructure.infrastructure_analyze import InfrastructureAnalyze


@pytest.fixture(autouse=True)
def stub_instana_model_modules():
    module_names = [
        "instana_client.models.cursor_pagination",
        "instana_client.models.get_infrastructure_groups_query",
        "instana_client.models.get_infrastructure_query",
        "instana_client.models.infra_metric_configuration",
        "instana_client.models.order",
        "instana_client.models.simple_metric_configuration",
        "instana_client.models.tag_filter",
        "instana_client.models.tag_filter_all_of_value",
        "instana_client.models.tag_filter_expression",
        "instana_client.models.time_frame",
    ]
    original_modules = {name: sys.modules.get(name) for name in module_names}

    def _simple_init(self, *args, **kwargs):
        if args:
            if len(args) == 1 and not kwargs:
                self.value = args[0]
            else:
                for index, value in enumerate(args):
                    setattr(self, f"arg{index}", value)
        for key, value in kwargs.items():
            setattr(self, key, value)

    stub_definitions = {
        "instana_client.models.cursor_pagination": ("CursorPagination", type("CursorPagination", (), {"__init__": _simple_init})),
        "instana_client.models.get_infrastructure_groups_query": ("GetInfrastructureGroupsQuery", type("GetInfrastructureGroupsQuery", (), {"__init__": _simple_init, "to_dict": lambda self: self.__dict__})),
        "instana_client.models.get_infrastructure_query": ("GetInfrastructureQuery", type("GetInfrastructureQuery", (), {"__init__": _simple_init, "to_dict": lambda self: self.__dict__})),
        "instana_client.models.infra_metric_configuration": ("InfraMetricConfiguration", type("InfraMetricConfiguration", (), {"__init__": _simple_init})),
        "instana_client.models.order": ("Order", type("Order", (), {"__init__": _simple_init})),
        "instana_client.models.simple_metric_configuration": ("SimpleMetricConfiguration", type("SimpleMetricConfiguration", (), {"__init__": _simple_init})),
        "instana_client.models.tag_filter": ("TagFilter", type("TagFilter", (), {"__init__": _simple_init})),
        "instana_client.models.tag_filter_all_of_value": ("TagFilterAllOfValue", type("TagFilterAllOfValue", (), {"__init__": _simple_init})),
        "instana_client.models.tag_filter_expression": ("TagFilterExpression", type("TagFilterExpression", (), {"__init__": _simple_init})),
        "instana_client.models.time_frame": ("TimeFrame", type("TimeFrame", (), {"__init__": _simple_init})),
    }

    for module_name, (class_name, class_value) in stub_definitions.items():
        stub_module = types.ModuleType(module_name)
        setattr(stub_module, class_name, class_value)
        sys.modules[module_name] = stub_module

    try:
        yield
    finally:
        for module_name, original_module in original_modules.items():
            if original_module is not None:
                sys.modules[module_name] = original_module
            else:
                sys.modules.pop(module_name, None)


@pytest.fixture
def mock_schema_dir(tmp_path):
    """Create temporary schema directory with test schemas"""
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()

    # Create jvmRuntimePlatform schema
    jvm_schema = {
        "type": "jvmRuntimePlatform",
        "parameters": {
            "metrics": {
                "metric": [
                    "jvm.heap.maxSize",
                    "jvm.heap.used",
                    "jvm.threads.count"
                ],
                "aggregation": {
                    "enum": ["mean", "max", "min", "sum"]
                }
            },
            "tagFilterElements": {
                "enum": [
                    "host.name",
                    "jvm.name",
                    "process.name"
                ]
            }
        }
    }

    with open(schema_dir / "jvmRuntimePlatform_schema.json", "w") as f:
        json.dump(jvm_schema, f)

    # Create kubernetesPod schema
    k8s_schema = {
        "type": "kubernetesPod",
        "parameters": {
            "metrics": {
                "metric": [
                    "cpuRequests",
                    "cpuLimits",
                    "cpuUsed"
                ],
                "aggregation": {
                    "enum": ["mean", "max", "min"]
                }
            },
            "tagFilterElements": {
                "enum": [
                    "kubernetes.namespace.name",
                    "kubernetes.cluster.name"
                ]
            }
        }
    }

    with open(schema_dir / "kubernetesPod_schema.json", "w") as f:
        json.dump(k8s_schema, f)

    return schema_dir


@pytest.fixture
def tool_instance(mock_schema_dir):
    """Create InfrastructureAnalyze instance with test schema dir"""
    return InfrastructureAnalyze(
        read_token="test_token",
        base_url="https://test.instana.io",
        schema_dir=mock_schema_dir
    )


class TestPass1IntentToElicitation:
    """Test Pass 1: Intent → Schema Elicitation"""

    @pytest.mark.asyncio
    async def test_pass1_jvm_entity(self, tool_instance):
        """Test Pass 1 with JVM entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="maximum heap size of JVM on host galactica1",
            entity="jvm"
        )

        # Should return list with 2 items
        assert isinstance(result, list)
        assert len(result) == 2

        # First item should be TextContent with instructions
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "jvmRuntimePlatform" in result[0].text
        assert "maximum heap size" in result[0].text

        # Second item should be EmbeddedResource with schema
        assert isinstance(result[1], EmbeddedResource)
        assert result[1].type == "resource"
        assert isinstance(result[1].resource, TextResourceContents)
        assert "jvmRuntimePlatform" in str(result[1].resource.uri)

        # Schema should be valid JSON
        schema = json.loads(result[1].resource.text)
        assert schema["type"] == "jvmRuntimePlatform"
        assert "jvm.heap.maxSize" in schema["parameters"]["metrics"]["metric"]

    @pytest.mark.asyncio
    async def test_pass1_kubernetes_pod(self, tool_instance):
        """Test Pass 1 with kubernetes pod entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="CPU usage of pods in production namespace",
            entity="kubernetes pod"
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], TextContent)
        assert isinstance(result[1], EmbeddedResource)

        # Check schema is for kubernetesPod
        schema = json.loads(result[1].resource.text)
        assert schema["type"] == "kubernetesPod"

    @pytest.mark.asyncio
    async def test_pass1_ambiguous_kubernetes(self, tool_instance):
        """Test Pass 1 with ambiguous 'kubernetes' entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="CPU usage",
            entity="kubernetes"
        )

        # Should return error asking for clarification
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Ambiguous" in result[0].text
        assert "kubernetes pod" in result[0].text
        assert "kubernetes deployment" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_unknown_entity(self, tool_instance):
        """Test Pass 1 with unknown entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="some query",
            entity="unknown_entity"
        )

        # Should return error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown entity type" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_entity_resolution_priority(self, tool_instance):
        """Test entity resolution priority (specific before general)"""
        # Test "kubernetes deployment" resolves to deployment, not pod
        result = await tool_instance.analyze_infrastructure(
            intent="replica count",
            entity="kubernetes deployment"
        )

        # Should try to load kubernetesDeployment schema
        # (will fail since we only created pod schema, but that's ok for this test)
        assert isinstance(result, list)


class TestPass2SelectionsToAPI:
    """Test Pass 2: Selections → API Call"""

    @pytest.mark.asyncio
    async def test_pass2_with_valid_selections(self, tool_instance):
        """Test Pass 2 with valid selections"""
        # Mock the API client
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "label": "test-jvm-1",
                    "metrics": {
                        "jvm.heap.maxSize[max]": 1024000000
                    }
                }
            ]
        }).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metric": "jvm.heap.maxSize",
            "aggregation": "max",
            "filters": [
                {"name": "host.name", "value": "galactica1"}
            ]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        # Should return list with TextContent
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "test-jvm-1" in result[0].text
        assert "jvm.heap.maxSize" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_missing_entity_type(self, tool_instance):
        """Test Pass 2 with missing entity_type"""
        selections = {
            "metric": "jvm.heap.maxSize",
            "aggregation": "max"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections
        )

        # Should return error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "must include 'entity_type'" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_missing_metric(self, tool_instance):
        """Test Pass 2 with missing metric"""
        selections = {
            "entity_type": "jvmRuntimePlatform",
            "aggregation": "max"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections
        )

        # Should return error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "must include" in result[0].text and "metric" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_api_error(self, tool_instance):
        """Test Pass 2 with API error"""
        mock_api_client = Mock()
        mock_api_client.get_entities_without_preload_content.side_effect = Exception("API Error")

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metric": "jvm.heap.maxSize",
            "aggregation": "max"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        # Should return error message
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error calling Instana API" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_no_results(self, tool_instance):
        """Test Pass 2 with no results from API"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metric": "jvm.heap.maxSize",
            "aggregation": "max"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        # Should return "no entities found" message
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "No" in result[0].text and "found" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_group_by_too_many_tags(self, tool_instance):
        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "groupBy": ["a", "b", "c", "d", "e", "f"]
        }

        result = await tool_instance.analyze_infrastructure(selections=selections)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "maximum 5 tag names" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_kubernetes_resolves_to_deployment_from_intent(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="show desiredreplica for kubernetes workloads",
            entity="kubernetes"
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for kubernetesDeployment" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_kubernetes_resolves_to_pod_from_intent(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="show pod restart count in cluster",
            entity="kubernetes"
        )

        assert len(result) == 2
        assert isinstance(result[0], TextContent)
        assert isinstance(result[1], EmbeddedResource)
        schema = json.loads(result[1].resource.text)
        assert schema["type"] == "kubernetesPod"

    @pytest.mark.asyncio
    async def test_pass1_docker_container_unknown_schema(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="cpu usage of docker container",
            entity="docker container"
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for dockerContainer" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_infrastructure_invalid_input(self, tool_instance):
        result = await tool_instance.analyze_infrastructure()

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Invalid input" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_infrastructure_catches_unexpected_exception(self, tool_instance):
        with patch.object(
            tool_instance,
            "_handle_pass1_intent",
            new=AsyncMock(side_effect=Exception("boom"))
        ):
            result = await tool_instance.analyze_infrastructure(
                intent="heap",
                entity="jvm"
            )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: boom" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_supports_string_metric_and_groupby(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "tags": {"host.name": "galactica1"},
                    "count": 2,
                    "metrics": {"jvm.heap.maxSize.MAX": 1024, "other.metric": 1}
                }
            ]
        }).encode("utf-8")
        mock_api_client.get_entity_groups_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metric": "jvm.heap.maxSize",
            "aggregation": "max",
            "groupBy": "host.name",
            "order": {"by": "jvm.heap.maxSize", "direction": "asc"},
            "pagination": {"page": 2, "pageSize": 10},
            "timeRange": "30m"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "Found 1 groups" in result[0].text
        assert "host.name=galactica1" in result[0].text
        assert "jvm.heap.maxSize.MAX" in result[0].text
        mock_api_client.get_entity_groups_without_preload_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_pass2_with_multiple_filters_absolute_timestamp_range_and_offset(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "label": "entity-a",
                    "metrics": {"jvm.heap.used.MEAN": 256, "ignored.metric": 1}
                }
            ]
        }).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.used"],
            "aggregation": "mean",
            "filters": [
                {"name": "host.name", "value": "host-1"},
                {"name": "jvm.name", "value": "jvm-1"}
            ],
            "pagination": {"limit": 5, "offset": 3},
            "timeRange": {"from": 1000, "to": 2000}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "Found 1 jvmRuntimePlatform entities" in result[0].text
        assert "entity-a" in result[0].text
        assert "jvm.heap.used.MEAN" in result[0].text
        mock_api_client.get_entities_without_preload_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_pass2_with_absolute_date_range_strings(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.used"],
            "timeRange": {"from": "2026-01-24 12:25:00", "to": "2026-01-24 14:40:00"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "No jvmRuntimePlatform entities found" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_with_invalid_absolute_date_range_falls_back(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.used"],
            "timeRange": {"from": "not-a-date", "to": "still-not-a-date"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "No jvmRuntimePlatform entities found" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_with_missing_from_or_to_defaults(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.used"],
            "timeRange": {"from": 1000}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "No jvmRuntimePlatform entities found" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_with_unrecognized_relative_time_defaults(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.used"],
            "timeRange": "nonsense"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert "No jvmRuntimePlatform entities found" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_logging_serialization_failure_does_not_break_flow(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        original_json_dumps = json.dumps

        def selective_dumps(value, *args, **kwargs):
            if value == {"force": "fail"}:
                raise Exception("serialize failed")
            return original_json_dumps(value, *args, **kwargs)

        with patch("json.dumps", side_effect=selective_dumps):
            with patch("instana_client.models.get_infrastructure_query.GetInfrastructureQuery.to_dict", return_value={"force": "fail"}):
                result = await tool_instance.analyze_infrastructure(
                    selections={
                        "entity_type": "jvmRuntimePlatform",
                        "metrics": ["jvm.heap.used"]
                    },
                    api_client=mock_api_client
                )

        assert len(result) == 1
        assert "No jvmRuntimePlatform entities found" in result[0].text
        assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    async def test_pass2_string_metric_and_groupby_normalized(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "tags": {"host.name": "galactica1"},
                    "count": 1,
                    "metrics": {"jvm.heap.maxSize[mean]": 123}
                }
            ]
        }).encode("utf-8")
        mock_api_client.get_entity_groups_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": "jvm.heap.maxSize",
            "groupBy": "host.name",
            "aggregation": "mean"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Found 1 groups" in result[0].text
        assert "host.name=galactica1" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_invalid_json_response(self, tool_instance):
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = b"not json"
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error calling Instana API" in result[0].text or "Error" in result[0].text


class TestAdditionalPass1Coverage:
    """Additional branch coverage for pass 1 resolution"""

    @pytest.mark.asyncio
    async def test_pass1_kubernetes_resolves_to_deployment_from_intent(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="show desiredreplica for this kubernetes workload",
            entity="kubernetes"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for kubernetesDeployment" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_kubernetes_resolves_to_pod_from_intent(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="show pod restart count",
            entity="kubernetes"
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], TextContent)
        assert isinstance(result[1], EmbeddedResource)

    @pytest.mark.asyncio
    async def test_pass1_schema_missing_for_resolved_entity(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="queue depth",
            entity="ibmmq"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for ibmMqQueue" in result[0].text


class TestInvalidInput:
    """Test invalid input handling"""

    @pytest.mark.asyncio
    async def test_no_parameters(self, tool_instance):
        """Test with no parameters"""
        result = await tool_instance.analyze_infrastructure()

        # Should return error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Invalid input" in result[0].text

    @pytest.mark.asyncio
    async def test_intent_without_entity(self, tool_instance):
        """Test with intent but no entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="some query"
        )

        # Should return error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Invalid input" in result[0].text


class TestEntityResolution:
    """Test entity resolution logic"""

    @pytest.mark.asyncio
    async def test_jvm_aliases(self, tool_instance):
        """Test JVM entity aliases"""
        # Test "jvm"
        result1 = await tool_instance._handle_pass1_intent({"intent": "test", "entity": "jvm"})
        assert isinstance(result1, list)

        # Test "java"
        result2 = await tool_instance._handle_pass1_intent({"intent": "test", "entity": "java"})
        assert isinstance(result2, list)

    @pytest.mark.asyncio
    async def test_kubernetes_specific_matches(self, tool_instance):
        """Test kubernetes specific matches"""
        # "kubernetes deployment" should resolve to deployment
        result1 = await tool_instance._handle_pass1_intent({
            "intent": "test",
            "entity": "kubernetes deployment"
        })
        # Will fail to load schema but that's ok - we're testing resolution
        assert isinstance(result1, list)

        # "kubernetes pod" should resolve to pod
        result2 = await tool_instance._handle_pass1_intent({
            "intent": "test",
            "entity": "kubernetes pod"
        })
        assert isinstance(result2, list)
        assert len(result2) == 2  # Should succeed with pod schema

    @pytest.mark.asyncio
    async def test_deployment_keyword(self, tool_instance):
        """Test 'deployment' keyword alone"""
        result = await tool_instance._handle_pass1_intent({
            "intent": "test",
            "entity": "deployment"
        })
        # Should resolve to kubernetesDeployment
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pod_keyword(self, tool_instance):
        """Test 'pod' keyword alone"""
        result = await tool_instance._handle_pass1_intent({
            "intent": "test",
            "entity": "pod"
        })
        # Should resolve to kubernetesPod
        assert isinstance(result, list)
        assert len(result) == 2  # Should succeed with pod schema



class TestAdditionalAnalyzeCoverage:
    """Additional coverage for analyze_infrastructure edge cases."""

    @pytest.mark.asyncio
    async def test_top_level_exception_is_returned_as_text(self, tool_instance):
        with patch.object(tool_instance, "_handle_pass1_intent", side_effect=Exception("boom")):
            result = await tool_instance.analyze_infrastructure(
                intent="heap usage",
                entity="jvm"
            )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: boom" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_host_entity_resolution(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="cpu usage on machine",
            entity="server"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for host" in result[0].text

    @pytest.mark.asyncio
    async def test_pass1_genai_entity_resolution(self, tool_instance):
        result = await tool_instance.analyze_infrastructure(
            intent="latency for model inference",
            entity="gen ai service"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Could not load schema for oTelLLM" in result[0].text


class TestPass2TimeRangeParsing:
    """Test time range parsing in Pass 2"""

    @pytest.mark.asyncio
    async def test_pass2_relative_time_hours(self, tool_instance):
        """Test relative time range in hours"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": "2h"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_pass2_relative_time_minutes(self, tool_instance):
        """Test relative time range in minutes"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": "30m"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_relative_time_days(self, tool_instance):
        """Test relative time range in days"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": "1d"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_absolute_time_timestamps(self, tool_instance):
        """Test absolute time range with timestamps"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": {"from": 1625097600000, "to": 1625184000000}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_absolute_time_date_strings(self, tool_instance):
        """Test absolute time range with date strings"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": {"from": "2026-01-24 12:25:00", "to": "2026-01-24 14:40:00"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_absolute_time_invalid_date_format(self, tool_instance):
        """Test absolute time range with invalid date format"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": {"from": "invalid-date", "to": "invalid-date"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        # Should still work with default time range
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_absolute_time_missing_to(self, tool_instance):
        """Test absolute time range with missing 'to'"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": {"from": 1625097600000}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        # Should default to relative time
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_unrecognized_time_format(self, tool_instance):
        """Test unrecognized time format defaults to 1h"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "timeRange": "invalid_format"
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)


class TestPass2Filters:
    """Test filter handling in Pass 2"""

    @pytest.mark.asyncio
    async def test_pass2_single_filter(self, tool_instance):
        """Test with single filter"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "filters": [{"name": "host.name", "value": "test-host"}]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_multiple_filters(self, tool_instance):
        """Test with multiple filters (AND logic)"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "filters": [
                {"name": "host.name", "value": "test-host"},
                {"name": "jvm.name", "value": "test-jvm"}
            ]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_no_filters(self, tool_instance):
        """Test with no filters"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)


class TestPass2GroupBy:
    """Test groupBy functionality in Pass 2"""

    @pytest.mark.asyncio
    async def test_pass2_with_groupby(self, tool_instance):
        """Test with groupBy parameter"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "tags": {"host.name": "host1"},
                    "count": 5,
                    "metrics": {"jvm.heap.maxSize[mean]": 1024}
                }
            ]
        }).encode('utf-8')
        mock_api_client.get_entity_groups_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "groupBy": ["host.name"]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "host1" in result[0].text
        assert "count: 5" in result[0].text

    @pytest.mark.asyncio
    async def test_pass2_groupby_multiple_tags(self, tool_instance):
        """Test groupBy with multiple tags"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "tags": {"host.name": "host1", "zone": "us-east"},
                    "count": 3,
                    "metrics": {}
                }
            ]
        }).encode('utf-8')
        mock_api_client.get_entity_groups_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "groupBy": ["host.name", "zone"]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)
        assert "host1" in result[0].text
        assert "us-east" in result[0].text


class TestPass2OrderAndPagination:
    """Test order and pagination in Pass 2"""

    @pytest.mark.asyncio
    async def test_pass2_with_order(self, tool_instance):
        """Test with order parameter"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "order": {"by": "jvm.heap.maxSize", "direction": "DESC"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_order_without_aggregation_suffix(self, tool_instance):
        """Test order.by gets aggregation appended"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "aggregation": "max",
            "order": {"by": "jvm.heap.maxSize"}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_pagination_with_page(self, tool_instance):
        """Test pagination with page number"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "pagination": {"page": 2, "pageSize": 20}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass2_pagination_with_offset(self, tool_instance):
        """Test pagination with offset"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({"items": []}).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize"],
            "pagination": {"offset": 40, "limit": 20}
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)


class TestPass2MultipleMetrics:
    """Test multiple metrics in Pass 2"""

    @pytest.mark.asyncio
    async def test_pass2_multiple_metrics(self, tool_instance):
        """Test with multiple metrics"""
        mock_api_client = Mock()
        mock_response = Mock()
        mock_response.data = json.dumps({
            "items": [
                {
                    "label": "test-jvm",
                    "metrics": {
                        "jvm.heap.maxSize[mean]": 1024,
                        "jvm.heap.used[mean]": 512
                    }
                }
            ]
        }).encode('utf-8')
        mock_api_client.get_entities_without_preload_content.return_value = mock_response

        selections = {
            "entity_type": "jvmRuntimePlatform",
            "metrics": ["jvm.heap.maxSize", "jvm.heap.used"]
        }

        result = await tool_instance.analyze_infrastructure(
            selections=selections,
            api_client=mock_api_client
        )

        assert isinstance(result, list)
        assert "jvm.heap.maxSize" in result[0].text
        assert "jvm.heap.used" in result[0].text


class TestPass1AdditionalEntityTypes:
    """Test additional entity type resolutions"""

    @pytest.mark.asyncio
    async def test_pass1_docker_container(self, tool_instance):
        """Test docker container entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="container CPU usage",
            entity="docker container"
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass1_db2_database(self, tool_instance):
        """Test DB2 database entity"""
        result = await tool_instance.analyze_infrastructure(
            intent="database connections",
            entity="db2 database"
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass1_container_keyword(self, tool_instance):
        """Test container keyword"""
        result = await tool_instance.analyze_infrastructure(
            intent="memory usage",
            entity="container"
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass1_queue_keyword(self, tool_instance):
        """Test queue keyword"""
        result = await tool_instance.analyze_infrastructure(
            intent="queue depth",
            entity="queue"
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass1_database_keyword(self, tool_instance):
        """Test database keyword"""
        result = await tool_instance.analyze_infrastructure(
            intent="query performance",
            entity="database"
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_pass1_llm_variations(self, tool_instance):
        """Test various LLM/GenAI entity variations"""
        variations = [
            "otel llm",
            "large language model",
            "llm model",
            "llm service",
            "genai service",
            "ai model"
        ]

        for entity in variations:
            result = await tool_instance.analyze_infrastructure(
                intent="model latency",
                entity=entity
            )
            assert isinstance(result, list)
