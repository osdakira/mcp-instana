"""
Unit tests for the InfrastructureAnalyzeMCPTools class
"""

import asyncio
import json
import logging
import os
import sys
import unittest
from functools import wraps
from unittest.mock import MagicMock, patch


# Create a null handler that will discard all log messages
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Configure root logger to use ERROR level and disable propagation
logging.basicConfig(level=logging.ERROR)

# Get the application logger and replace its handlers
app_logger = logging.getLogger('src.infrastructure.infrastructure_analyze')
app_logger.handlers = []
app_logger.addHandler(NullHandler())
app_logger.propagate = False  # Prevent logs from propagating to parent loggers

# Suppress traceback printing for expected test exceptions
import traceback

original_print_exception = traceback.print_exception
original_print_exc = traceback.print_exc

def custom_print_exception(etype, value, tb, limit=None, file=None, chain=True):
    # Skip printing exceptions from the mock side_effect
    if isinstance(value, Exception) and str(value) == "Test error":
        return
    original_print_exception(etype, value, tb, limit, file, chain)

def custom_print_exc(limit=None, file=None, chain=True):
    # Just do nothing - this will suppress all traceback printing from print_exc
    pass

traceback.print_exception = custom_print_exception
traceback.print_exc = custom_print_exc

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Just pass the API client directly
            kwargs['api_client'] = self.analyze_api
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

# Create mock modules and classes
sys.modules['instana_client'] = MagicMock()
sys.modules['instana_client.api'] = MagicMock()
sys.modules['instana_client.api.infrastructure_analyze_api'] = MagicMock()
sys.modules['instana_client.configuration'] = MagicMock()
sys.modules['instana_client.api_client'] = MagicMock()
sys.modules['instana_client.models'] = MagicMock()
sys.modules['instana_client.models.get_available_metrics_query'] = MagicMock()
sys.modules['instana_client.models.get_available_plugins_query'] = MagicMock()
sys.modules['instana_client.models.get_infrastructure_query'] = MagicMock()
sys.modules['instana_client.models.get_infrastructure_groups_query'] = MagicMock()

# Set up mock classes
mock_configuration = MagicMock()
mock_api_client = MagicMock()
mock_analyze_api = MagicMock()
mock_metrics_query = MagicMock()
mock_plugins_query = MagicMock()
mock_infra_query = MagicMock()
mock_groups_query = MagicMock()

# Add __name__ attribute to mock classes
mock_analyze_api.__name__ = "InfrastructureAnalyzeApi"
mock_metrics_query.__name__ = "GetAvailableMetricsQuery"
mock_plugins_query.__name__ = "GetAvailablePluginsQuery"
mock_infra_query.__name__ = "GetInfrastructureQuery"
mock_groups_query.__name__ = "GetInfrastructureGroupsQuery"

sys.modules['instana_client.configuration'].Configuration = mock_configuration
sys.modules['instana_client.api_client'].ApiClient = mock_api_client
sys.modules['instana_client.api.infrastructure_analyze_api'].InfrastructureAnalyzeApi = mock_analyze_api
sys.modules['instana_client.models.get_available_metrics_query'].GetAvailableMetricsQuery = mock_metrics_query
sys.modules['instana_client.models.get_available_plugins_query'].GetAvailablePluginsQuery = mock_plugins_query
sys.modules['instana_client.models.get_infrastructure_query'].GetInfrastructureQuery = mock_infra_query
sys.modules['instana_client.models.get_infrastructure_groups_query'].GetInfrastructureGroupsQuery = mock_groups_query

# Patch the with_header_auth decorator
with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    # Import the class to test (module was renamed to infrastructure_analyze_old)
    from src.infrastructure.infrastructure_analyze_old import (
        InfrastructureAnalyzeMCPTools,
    )

class TestInfrastructureAnalyzeMCPTools(unittest.TestCase):
    """Test the InfrastructureAnalyzeMCPTools class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset all mocks
        mock_configuration.reset_mock()
        mock_api_client.reset_mock()
        mock_analyze_api.reset_mock()
        mock_metrics_query.reset_mock()
        mock_plugins_query.reset_mock()
        mock_infra_query.reset_mock()
        mock_groups_query.reset_mock()

        # Store references to the global mocks
        self.mock_configuration = mock_configuration
        self.mock_api_client = mock_api_client
        self.analyze_api = MagicMock()

        # Create the client
        self.read_token = "test_token"
        self.base_url = "https://test.instana.io"
        self.client = InfrastructureAnalyzeMCPTools(read_token=self.read_token, base_url=self.base_url)

        # Set up the client's API attribute
        self.client.analyze_api = self.analyze_api

    def test_init(self):
        """Test that the client is initialized with the correct values"""
        self.assertEqual(self.client.read_token, self.read_token)
        self.assertEqual(self.client.base_url, self.base_url)

    def test_get_available_metrics_with_dict_payload(self):
        """Test get_available_metrics with a dictionary payload"""
        # Set up the mock response
        mock_result = {
            "metrics": [
                {"name": "memory.used", "unit": "bytes"},
                {"name": "cpu.usage", "unit": "percent"}
            ]
        }
        self.analyze_api.get_available_metrics.return_value = mock_result

        # Create a test payload
        payload = {
            "timeFrame": {
                "from": 1625097600000,
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        }

        # Call the method
        result = asyncio.run(self.client.get_available_metrics(payload=payload))

        # Check that the API was called
        self.analyze_api.get_available_metrics.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_available_metrics_with_string_payload(self):
        """Test get_available_metrics with a string payload"""
        # Set up the mock response
        mock_result = {
            "metrics": [
                {"name": "memory.used", "unit": "bytes"},
                {"name": "cpu.usage", "unit": "percent"}
            ]
        }
        self.analyze_api.get_available_metrics.return_value = mock_result

        # Create a test payload as a string
        payload = json.dumps({
            "timeFrame": {
                "from": 1625097600000,
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        })

        # Call the method
        result = asyncio.run(self.client.get_available_metrics(payload=payload))

        # Check that the API was called
        self.analyze_api.get_available_metrics.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_available_metrics_error_parsing_payload(self):
        """Test get_available_metrics with an invalid string payload"""
        # Create an invalid test payload
        payload = "This is not valid JSON or Python literal"

        # Call the method
        result = asyncio.run(self.client.get_available_metrics(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Invalid payload format", result["error"])

    def test_get_available_metrics_api_error(self):
        """Test get_available_metrics with API error"""
        # Set up the mock API to raise an exception
        self.analyze_api.get_available_metrics.side_effect = Exception("Test error")

        # Create a test payload
        payload = {
            "timeFrame": {
                "from": 1625097600000,
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        }

        # Call the method
        result = asyncio.run(self.client.get_available_metrics(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Failed to get available metrics", result["error"])

    def test_get_entities_with_dict_payload(self):
        """Test get_entities with a dictionary payload"""
        # Set up the mock response
        mock_result = {
            "items": [
                {
                    "id": "entity1",
                    "label": "Entity 1",
                    "metrics": {
                        "memory.used": [{"value": 1024}]
                    }
                },
                {
                    "id": "entity2",
                    "label": "Entity 2",
                    "metrics": {
                        "memory.used": [{"value": 2048}]
                    }
                }
            ]
        }
        self.analyze_api.get_entities.return_value = mock_result

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "metrics": [
                {"metric": "memory.used", "granularity": 3600000, "aggregation": "MAX"}
            ]
        }

        # Call the method
        result = asyncio.run(self.client.get_entities(payload=payload))

        # Check that the API was called
        self.analyze_api.get_entities.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_entities_with_string_payload(self):
        """Test get_entities with a string payload"""
        # Set up the mock response
        mock_result = {
            "items": [
                {
                    "id": "entity1",
                    "label": "Entity 1",
                    "metrics": {
                        "memory.used": [{"value": 1024}]
                    }
                }
            ]
        }
        self.analyze_api.get_entities.return_value = mock_result

        # Create a test payload as a string
        payload = json.dumps({
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "metrics": [
                {"metric": "memory.used", "granularity": 3600000, "aggregation": "MAX"}
            ]
        })

        # Call the method
        result = asyncio.run(self.client.get_entities(payload=payload))

        # Check that the API was called
        self.analyze_api.get_entities.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_entities_api_error(self):
        """Test get_entities with API error"""
        # Set up the mock API to raise an exception
        self.analyze_api.get_entities.side_effect = Exception("Test error")

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "type": "jvmRuntimePlatform",
            "metrics": [
                {"metric": "memory.used", "granularity": 3600000, "aggregation": "MAX"}
            ]
        }

        # Call the method
        result = asyncio.run(self.client.get_entities(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Failed to get entities", result["error"])

    def test_get_aggregated_entity_groups_with_dict_payload(self):
        """Test get_aggregated_entity_groups with a dictionary payload"""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.data = json.dumps({
            "items": [
                {
                    "tags": {
                        "host.name": "host1"
                    },
                    "metrics": {
                        "memory.used": [{"value": 1024}]
                    }
                },
                {
                    "tags": {
                        "host.name": "host2"
                    },
                    "metrics": {
                        "memory.used": [{"value": 2048}]
                    }
                }
            ]
        }).encode('utf-8')

        self.analyze_api.get_entity_groups_without_preload_content.return_value = mock_response

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "groupBy": ["host.name"],
            "type": "jvmRuntimePlatform",
            "metrics": [
                {"metric": "memory.used", "granularity": 3600000, "aggregation": "MEAN"}
            ],
            "pagination": {
                "retrievalSize": 20
            },
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        }

        # Call the method
        result = asyncio.run(self.client.get_aggregated_entity_groups(payload=payload))

        # Check that the API was called
        self.analyze_api.get_entity_groups_without_preload_content.assert_called_once()

        # Check that the result contains the expected data
        self.assertIn("hosts", result)
        self.assertEqual(len(result["hosts"]), 2)
        self.assertIn("host1", result["hosts"])
        self.assertIn("host2", result["hosts"])
        self.assertEqual(result["count"], 2)
        self.assertIn("summary", result)

    def test_get_aggregated_entity_groups_no_payload(self):
        """Test get_aggregated_entity_groups with no payload"""
        # Call the method with no payload
        result = asyncio.run(self.client.get_aggregated_entity_groups(payload=None))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertEqual("Payload is required for this operation", result["error"])

    def test_get_aggregated_entity_groups_api_error(self):
        """Test get_aggregated_entity_groups with API error"""
        # Set up the mock API to raise an exception
        self.analyze_api.get_entity_groups_without_preload_content.side_effect = Exception("Test error")

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "groupBy": ["host.name"],
            "type": "jvmRuntimePlatform",
            "metrics": [
                {"metric": "memory.used", "granularity": 3600000, "aggregation": "MEAN"}
            ],
            "pagination": {
                "retrievalSize": 20
            },
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        }

        # Call the method
        result = asyncio.run(self.client.get_aggregated_entity_groups(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("API call failed", result["error"])

    def test_summarize_entity_groups_result(self):
        """Test _summarize_entity_groups_result method"""
        # Create a test result dictionary
        result_dict = {
            "items": [
                {
                    "tags": {
                        "host.name": "host1"
                    }
                },
                {
                    "tags": {
                        "host.name": "host3"
                    }
                },
                {
                    "tags": {
                        "host.name": "host2"
                    }
                }
            ]
        }

        # Create a test query body
        query_body = {
            "groupBy": ["host.name"]
        }

        # Call the method
        result = self.client._summarize_entity_groups_result(result_dict, query_body)

        # Check that the result contains the expected data
        self.assertIn("hosts", result)
        self.assertEqual(len(result["hosts"]), 3)
        # Check that hosts are sorted alphabetically
        self.assertEqual(result["hosts"], ["host1", "host2", "host3"])
        self.assertEqual(result["count"], 3)
        self.assertIn("summary", result)
        self.assertIn("Found 3 hosts", result["summary"])

    def test_get_available_plugins_with_dict_payload(self):
        """Test get_available_plugins with a dictionary payload"""
        # Set up the mock response
        mock_result = {
            "plugins": [
                {"name": "jvmRuntimePlatform", "type": "java"},
                {"name": "docker", "type": "container"}
            ]
        }
        self.analyze_api.get_available_plugins.return_value = mock_result

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "query": "java",
            "offline": False,
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        }

        # Call the method
        result = asyncio.run(self.client.get_available_plugins(payload=payload))

        # Check that the API was called
        self.analyze_api.get_available_plugins.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_available_plugins_with_string_payload(self):
        """Test get_available_plugins with a string payload"""
        # Set up the mock response
        mock_result = {
            "plugins": [
                {"name": "jvmRuntimePlatform", "type": "java"}
            ]
        }
        self.analyze_api.get_available_plugins.return_value = mock_result

        # Create a test payload as a string
        payload = json.dumps({
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "query": "java",
            "offline": False,
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            }
        })

        # Call the method
        result = asyncio.run(self.client.get_available_plugins(payload=payload))

        # Check that the API was called
        self.analyze_api.get_available_plugins.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_available_plugins_api_error(self):
        """Test get_available_plugins with API error"""
        # Set up the mock API to raise an exception
        self.analyze_api.get_available_plugins.side_effect = Exception("Test error")

        # Create a test payload
        payload = {
            "timeFrame": {
                "to": 1625184000000,
                "windowSize": 3600000
            },
            "query": "java",
            "offline": False
        }

        # Call the method
        result = asyncio.run(self.client.get_available_plugins(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Failed to get available plugins", result["error"])

    def test_get_available_metrics_with_none_payload(self):
        """Test get_available_metrics with None payload"""
        # Set up the mock response
        mock_result = {"metrics": []}
        self.analyze_api.get_available_metrics.return_value = mock_result

        # Call the method with None payload
        result = asyncio.run(self.client.get_available_metrics(payload=None))

        # Check that the API was called
        self.analyze_api.get_available_metrics.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_entities_with_none_payload(self):
        """Test get_entities with None payload"""
        # Call the method with None payload
        result = asyncio.run(self.client.get_entities(payload=None))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Failed to create GetInfrastructureQuery object", result["error"])

    def test_get_available_plugins_with_none_payload(self):
        """Test get_available_plugins with None payload"""
        # Set up the mock response
        mock_result = {"plugins": []}
        self.analyze_api.get_available_plugins.return_value = mock_result

        # Call the method with None payload
        result = asyncio.run(self.client.get_available_plugins(payload=None))

        # Check that the API was called
        self.analyze_api.get_available_plugins.assert_called_once()

        # Check that the result is correct
        self.assertEqual(result, mock_result)

    def test_get_aggregated_entity_groups_http_error(self):
        """Test get_aggregated_entity_groups with HTTP error response"""
        # Set up the mock response with error status
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.data = b"Not Found"

        self.analyze_api.get_entity_groups_without_preload_content.return_value = mock_response

        # Create a test payload
        payload = {
            "timeFrame": {"to": 1625184000000, "windowSize": 3600000},
            "groupBy": ["host.name"],
            "type": "jvmRuntimePlatform"
        }

        # Call the method
        result = asyncio.run(self.client.get_aggregated_entity_groups(payload=payload))

        # Check that the result contains an error message
        self.assertIn("error", result)
        self.assertIn("Failed to get entity groups: HTTP 404", result["error"])

    def test_summarize_entity_groups_result_with_error(self):
        """Test _summarize_entity_groups_result with error in result"""
        # Create a test result dictionary with error
        result_dict = {"error": "API error occurred"}

        # Create a test query body
        query_body = {"groupBy": ["host.name"]}

        # Call the method
        result = self.client._summarize_entity_groups_result(result_dict, query_body)

        # Check that the error is returned as is
        self.assertEqual(result, result_dict)

    def test_summarize_entity_groups_result_with_no_items(self):
        """Test _summarize_entity_groups_result with no items"""
        # Create a test result dictionary with no items
        result_dict = {"items": []}

        # Create a test query body
        query_body = {"groupBy": ["host.name"]}

        # Call the method
        result = self.client._summarize_entity_groups_result(result_dict, query_body)

        # Check that the result contains empty hosts list
        self.assertIn("hosts", result)
        self.assertEqual(len(result["hosts"]), 0)
        self.assertEqual(result["count"], 0)

    def test_debug_print_writes_to_stderr(self):
        """Test debug_print writes to stderr."""
        from src.infrastructure.infrastructure_analyze_old import debug_print

        with patch("sys.stderr") as mock_stderr:
            debug_print("hello", end="!")
            mock_stderr.write.assert_called()

    def test_get_available_metrics_parses_python_literal_string(self):
        """Test get_available_metrics falls back to ast.literal_eval."""
        self.analyze_api.get_available_metrics.return_value = {"metrics": ["ok"]}

        payload = "{'timeFrame': {'to': 1, 'from': 0, 'windowSize': 1}, 'type': 'jvmRuntimePlatform'}"

        result = asyncio.run(self.client.get_available_metrics(payload=payload))

        self.assertEqual(result, {"metrics": ["ok"]})
        self.analyze_api.get_available_metrics.assert_called_once()

    def test_get_available_metrics_parse_failure_returns_failed_to_parse_payload(self):
        """Test get_available_metrics outer parse exception path."""
        with patch("json.loads", side_effect=RuntimeError("json boom")):
            result = asyncio.run(self.client.get_available_metrics(payload='{"type": "jvmRuntimePlatform"}'))

        self.assertEqual(
            result,
            {
                "error": "Failed to parse payload: json boom",
                "payload": '{"type": "jvmRuntimePlatform"}',
            },
        )

    def test_get_available_metrics_import_error_returns_error(self):
        """Test get_available_metrics import error branch."""
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "instana_client.models.get_available_metrics_query":
                raise ImportError("missing metrics query")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            result = asyncio.run(self.client.get_available_metrics(payload={}))

        self.assertIn("error", result)
        self.assertIn("Error importing GetAvailableMetricsQuery", result["error"])

    def test_get_available_metrics_query_object_creation_error(self):
        """Test get_available_metrics query object creation failure."""
        mock_metrics_query.side_effect = Exception("bad metrics model")
        try:
            result = asyncio.run(
                self.client.get_available_metrics(
                    payload={"type": "jvmRuntimePlatform"}
                )
            )
        finally:
            mock_metrics_query.side_effect = None

        self.assertTrue(hasattr(result, "to_dict"))

    def test_get_available_metrics_result_uses_to_dict_when_available(self):
        """Test get_available_metrics converts model result with to_dict."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"metrics": ["converted"]}
        self.analyze_api.get_available_metrics.return_value = mock_result

        result = asyncio.run(
            self.client.get_available_metrics(payload={"type": "jvmRuntimePlatform"})
        )

        self.assertEqual(result, {"metrics": ["converted"]})

    def test_get_entities_parses_python_literal_string(self):
        """Test get_entities falls back to ast.literal_eval."""
        self.analyze_api.get_entities.return_value = {"items": ["ok"]}

        payload = "{'type': 'jvmRuntimePlatform', 'metrics': [{'metric': 'memory.used'}]}"

        result = asyncio.run(self.client.get_entities(payload=payload))

        self.assertEqual(result, {"items": ["ok"]})

    def test_get_entities_parse_failure_returns_failed_to_parse_payload(self):
        """Test get_entities outer parse exception path."""
        with patch("json.loads", side_effect=RuntimeError("json boom")):
            result = asyncio.run(self.client.get_entities(payload='{"type": "jvmRuntimePlatform"}'))

        self.assertEqual(
            result,
            {
                "error": "Failed to parse payload: json boom",
                "payload": '{"type": "jvmRuntimePlatform"}',
            },
        )

    def test_get_entities_result_uses_to_dict_when_available(self):
        """Test get_entities converts model result with to_dict."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"items": ["converted"]}
        self.analyze_api.get_entities.return_value = mock_result

        result = asyncio.run(
            self.client.get_entities(payload={"type": "jvmRuntimePlatform", "metrics": []})
        )

        self.assertEqual(result, {"items": ["converted"]})

    def test_get_aggregated_entity_groups_parses_python_literal_string(self):
        """Test get_aggregated_entity_groups falls back to ast.literal_eval."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.data = json.dumps({"items": []}).encode("utf-8")
        self.analyze_api.get_entity_groups_without_preload_content.return_value = mock_response

        payload = "{'groupBy': ['host.name'], 'type': 'jvmRuntimePlatform'}"

        result = asyncio.run(self.client.get_aggregated_entity_groups(payload=payload))

        self.assertIn("hosts", result)
        self.assertEqual(result["count"], 0)

    def test_get_aggregated_entity_groups_parse_failure_returns_failed_to_parse_payload(self):
        """Test get_aggregated_entity_groups outer parse exception path."""
        with patch("json.loads", side_effect=RuntimeError("json boom")):
            result = asyncio.run(
                self.client.get_aggregated_entity_groups(payload='{"groupBy": ["host.name"]}')
            )

        self.assertEqual(
            result,
            {
                "error": "Failed to parse payload: json boom",
                "payload": '{"groupBy": ["host.name"]}',
            },
        )

    def test_get_aggregated_entity_groups_model_creation_error(self):
        """Test get_aggregated_entity_groups model creation failure."""
        mock_groups_query.side_effect = Exception("bad groups model")
        try:
            result = asyncio.run(
                self.client.get_aggregated_entity_groups(
                    payload={"groupBy": ["host.name"], "type": "jvmRuntimePlatform"}
                )
            )
        finally:
            mock_groups_query.side_effect = None

        self.assertIn("error", result)
        self.assertIn("Failed to get entity groups", result["error"])

    def test_get_aggregated_entity_groups_top_level_exception(self):
        """Test get_aggregated_entity_groups API-call exception branch."""
        with patch.object(self.client, "_summarize_entity_groups_result", side_effect=Exception("summary boom")):
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.data = json.dumps({"items": []}).encode("utf-8")
            self.analyze_api.get_entity_groups_without_preload_content.return_value = mock_response

            result = asyncio.run(
                self.client.get_aggregated_entity_groups(
                    payload={"groupBy": ["host.name"], "type": "jvmRuntimePlatform"}
                )
            )

        self.assertEqual(
            result,
            {"error": "API call failed: summary boom"},
        )

    def test_summarize_entity_groups_result_handles_tag_dict_name(self):
        """Test summary extraction when tag value is a dict with name."""
        result = self.client._summarize_entity_groups_result(
            {
                "items": [
                    {"tags": {"host.name": {"name": "host-from-dict"}}},
                ]
            },
            {"groupBy": ["host.name"]},
        )

        self.assertEqual(result["hosts"], ["host-from-dict"])

    def test_summarize_entity_groups_result_converts_non_string_tag_values(self):
        """Test summary extraction converts non-string tag values."""
        result = self.client._summarize_entity_groups_result(
            {
                "items": [
                    {"tags": {"host.name": 123}},
                    {"tags": {"host.name": 123}},
                ]
            },
            {"groupBy": ["host.name"]},
        )

        self.assertEqual(result["hosts"], ["123"])
        self.assertEqual(result["count"], 1)

    def test_summarize_entity_groups_result_returns_error_on_exception(self):
        """Test summary exception branch returns error payload."""
        result = self.client._summarize_entity_groups_result(
            {"items": [object()]},
            {"groupBy": "not-a-list"},
        )

        self.assertIn("error", result)
        self.assertIn("Failed to summarize results", result["error"])

    def test_get_available_plugins_parses_python_literal_string(self):
        """Test get_available_plugins falls back to ast.literal_eval."""
        self.analyze_api.get_available_plugins.return_value = {"plugins": ["ok"]}

        payload = "{'query': 'java', 'offline': False}"

        result = asyncio.run(self.client.get_available_plugins(payload=payload))

        self.assertEqual(result, {"plugins": ["ok"]})

    def test_get_available_plugins_parse_failure_returns_failed_to_parse_payload(self):
        """Test get_available_plugins outer parse exception path."""
        with patch("json.loads", side_effect=RuntimeError("json boom")):
            result = asyncio.run(self.client.get_available_plugins(payload='{"query": "java"}'))

        self.assertEqual(
            result,
            {
                "error": "Failed to parse payload: json boom",
                "payload": '{"query": "java"}',
            },
        )

    def test_get_available_plugins_import_error_returns_error(self):
        """Test get_available_plugins import error branch."""
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "instana_client.models.get_available_plugins_query":
                raise ImportError("missing plugins query")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            result = asyncio.run(self.client.get_available_plugins(payload={}))

        self.assertEqual(
            result,
            {"error": "Failed to import GetAvailablePluginsQuery: missing plugins query"},
        )

    def test_get_available_plugins_query_object_creation_error(self):
        """Test get_available_plugins query object creation failure."""
        mock_plugins_query.side_effect = Exception("bad plugins model")
        try:
            result = asyncio.run(
                self.client.get_available_plugins(payload={"query": "java"})
            )
        finally:
            mock_plugins_query.side_effect = None

        self.assertTrue(hasattr(result, "to_dict"))

    def test_get_available_plugins_result_uses_to_dict_when_available(self):
        """Test get_available_plugins converts model result with to_dict."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"plugins": ["converted"]}
        self.analyze_api.get_available_plugins.return_value = mock_result

        result = asyncio.run(
            self.client.get_available_plugins(payload={"query": "java"})
        )

        self.assertEqual(result, {"plugins": ["converted"]})


if __name__ == '__main__':
    unittest.main()
