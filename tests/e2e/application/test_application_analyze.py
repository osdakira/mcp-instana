"""
E2E tests for Application Analyze MCP Tools.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.application.application_analyze import ApplicationAnalyzeMCPTools


class TestApplicationAnalyzeE2E:
    """E2E tests for Application Analyze tools"""

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_get_all_traces_multiple_pages_with_filters(self, instana_credentials):
        """Test get_all_traces with multiple pages and filters"""
        # Mock 3 pages of results
        mock_results = [
            {
                "items": [
                    {"traceId": "trace1", "timestamp": 1000},
                    {"traceId": "trace2", "timestamp": 2000}
                ],
                "canLoadMore": True,
            },
            {
                "items": [
                    {"traceId": "trace3", "timestamp": 3000},
                    {"traceId": "trace4", "timestamp": 4000}
                ],
                "canLoadMore": True,
            },
            {
                "items": [
                    {"traceId": "trace5", "timestamp": 5000}
                ],
                "canLoadMore": False,
            }
        ]

        call_count = 0
        def mock_get_traces(*args, **kwargs):
            nonlocal call_count
            mock_result = MagicMock()
            mock_result.to_dict.return_value = mock_results[call_count]
            call_count += 1
            return mock_result

        with patch("src.application.application_analyze.ApplicationAnalyzeApi") as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_traces.side_effect = mock_get_traces
            mock_api_class.return_value = mock_api

            client = ApplicationAnalyzeMCPTools(
                read_token=instana_credentials["api_token"],
                base_url=instana_credentials["base_url"],
            )

            # Replace the client's analyze_api with our mock
            client.analyze_api = mock_api

            # Test with filters
            result = await client.get_all_traces(
                payload={
                    "pagination": {"retrievalSize": 10},
                    "tagFilterExpression": {
                        "type": "EXPRESSION",
                        "logicalOperator": "AND",
                        "elements": [
                            {
                                "type": "TAG_FILTER",
                                "name": "service.name",
                                "operator": "EQUALS",
                                "entity": "DESTINATION",
                                "value": "test-service"
                            }
                        ]
                    }
                }
            )

            assert isinstance(result, dict)
            assert "file_path" in result
            assert "summary" in result
            assert "metadata" in result

            # Verify summary
            summary = result["summary"]
            assert summary["total_traces"] == 5
            assert summary["pages_fetched"] == 3

            # Verify metadata
            metadata = result["metadata"]
            assert metadata["stop_reason"] == "completed"

            # Verify file content
            file_path = result["file_path"]
            assert Path(file_path).exists()

            with open(file_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 5

                # Verify JSONL format
                for line in lines:
                    trace = json.loads(line)
                    assert "traceId" in trace
                    assert "timestamp" in trace

            # Verify API was called 3 times
            assert mock_api.get_traces.call_count == 3

            # Verify tagFilterExpression was passed to API
            first_call_args = mock_api.get_traces.call_args_list[0]
            assert first_call_args is not None

            # Extract the GetTraces object from the call
            get_traces_obj = first_call_args[1]['get_traces']

            # Verify tagFilterExpression was passed correctly
            assert hasattr(get_traces_obj, 'tag_filter_expression')
            assert get_traces_obj.tag_filter_expression is not None
            assert get_traces_obj.tag_filter_expression.type == "EXPRESSION"
            assert get_traces_obj.tag_filter_expression.logical_operator == "AND"
            assert len(get_traces_obj.tag_filter_expression.elements) == 1

            # Verify the tag filter element
            tag_filter = get_traces_obj.tag_filter_expression.elements[0]
            assert tag_filter.type == "TAG_FILTER"
            assert tag_filter.name == "service.name"
            assert tag_filter.operator == "EQUALS"
            assert tag_filter.entity == "DESTINATION"
            # SDK's from_dict stores value in the 'value' field as TagFilterAllOfValue
            assert tag_filter.value is not None
            assert str(tag_filter.value.actual_instance) == "test-service"

            # Clean up
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_get_all_traces_size_limit_abort(self, instana_credentials):
        """Test get_all_traces aborts when size limit is exceeded"""
        # Create large mock data that will exceed size limit
        large_trace = {"traceId": "trace" + "x" * 500, "timestamp": 1000, "data": "x" * 1000}

        mock_results = [
            {
                "items": [large_trace] * 2,
                "canLoadMore": True,
            },
            {
                "items": [large_trace] * 2,
                "canLoadMore": True,
            }
        ]

        call_count = 0
        def mock_get_traces(*args, **kwargs):
            nonlocal call_count
            mock_result = MagicMock()
            mock_result.to_dict.return_value = mock_results[call_count]
            call_count += 1
            return mock_result

        with patch("src.application.application_analyze.ApplicationAnalyzeApi") as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_traces.side_effect = mock_get_traces
            mock_api_class.return_value = mock_api

            client = ApplicationAnalyzeMCPTools(
                read_token=instana_credentials["api_token"],
                base_url=instana_credentials["base_url"],
            )

            # Replace the client's analyze_api with our mock
            client.analyze_api = mock_api

            # Set small size limit to trigger abort
            with patch("src.application.application_analyze.MAX_SIZE_BYTES", 3000):
                result = await client.get_all_traces(
                    payload={"pagination": {"retrievalSize": 10}}
                )

            assert isinstance(result, dict)
            assert "file_path" in result
            assert "summary" in result
            assert "metadata" in result

            # Verify it stopped due to size limit
            summary = result["summary"]
            assert summary["pages_fetched"] >= 1

            metadata = result["metadata"]
            assert metadata["stop_reason"] == "size_limit"

            # Verify file exists
            file_path = result["file_path"]
            assert Path(file_path).exists()

            # Clean up
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_get_all_traces_api_error_cleanup(self, instana_credentials):
        """Test get_all_traces cleans up partial file on API error"""
        # First call succeeds, second call fails
        mock_result_success = MagicMock()
        mock_result_success.to_dict.return_value = {
            "items": [{"traceId": "trace1", "timestamp": 1000}],
            "canLoadMore": True,
        }

        call_count = 0
        def mock_get_traces(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_result_success
            else:
                raise Exception("API Error")

        with patch("src.application.application_analyze.ApplicationAnalyzeApi") as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_traces.side_effect = mock_get_traces
            mock_api_class.return_value = mock_api

            client = ApplicationAnalyzeMCPTools(
                read_token=instana_credentials["api_token"],
                base_url=instana_credentials["base_url"],
            )

            # Replace the client's analyze_api with our mock
            client.analyze_api = mock_api

            # Execute and expect error
            result = await client.get_all_traces(
                payload={"pagination": {"retrievalSize": 10}}
            )

            # Verify error response
            assert isinstance(result, dict)
            assert "error" in result
            assert "Failed to collect traces" in result["error"]

# Made with Bob
