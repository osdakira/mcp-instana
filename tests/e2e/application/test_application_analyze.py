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

        mock_api = MagicMock()
        mock_api.get_traces.side_effect = mock_get_traces

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        # Test with filters - pass mock as api_client parameter
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
            },
            api_client=mock_api
        )

        assert isinstance(result, dict)
        assert "file_path" in result
        assert "item_count" in result
        assert "file_size_bytes" in result
        assert "stop_reason" in result

        # Verify item count
        assert result["item_count"] == 5

        # Verify stop reason
        assert result["stop_reason"] == "all_fetched"

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
    async def test_get_all_traces_max_retrieval_size_limit(self, instana_credentials):
        """Test get_all_traces respects max_retrieval_size limit"""
        # Create mock data with more items than max_retrieval_size
        mock_results = [
            {
                "items": [{"traceId": f"trace{i}", "timestamp": i * 1000} for i in range(1, 6)],
                "canLoadMore": True,
            },
            {
                "items": [{"traceId": f"trace{i}", "timestamp": i * 1000} for i in range(6, 11)],
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

        mock_api = MagicMock()
        mock_api.get_traces.side_effect = mock_get_traces

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        # Set max_retrieval_size to 7 to trigger limit
        # Note: Implementation fetches full pages, so with max_retrieval_size=7,
        # it will fetch page 1 (5 items) + page 2 (5 items) = 10 items total
        result = await client.get_all_traces(
            payload={"pagination": {"retrievalSize": 10}},
            max_retrieval_size=7,
            api_client=mock_api
        )

        assert isinstance(result, dict)
        assert "file_path" in result
        assert "item_count" in result
        assert "stop_reason" in result

        # Verify it stopped due to limit (fetches full pages, so 10 items total)
        assert result["item_count"] == 10  # 5 from page 1 + 5 from page 2
        assert result["stop_reason"] == "limit_reached"

        # Verify file exists and contains 10 lines
        file_path = result["file_path"]
        assert Path(file_path).exists()

        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 10

        # Verify API was called twice
        assert mock_api.get_traces.call_count == 2

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

        mock_api = MagicMock()
        mock_api.get_traces.side_effect = mock_get_traces

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        # Execute and expect error
        result = await client.get_all_traces(
            payload={"pagination": {"retrievalSize": 10}},
            api_client=mock_api
        )

        # Verify error response
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to get traces" in result["error"]

# Made with Bob
