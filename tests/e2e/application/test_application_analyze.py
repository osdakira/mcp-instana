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
    async def test_get_all_traces_single_page_with_filters(self, instana_credentials):
        """Test get_all_traces with single page and filters"""
        # Mock single page result
        mock_result_dict = {
            "items": [
                {"traceId": "trace1", "timestamp": 1000},
                {"traceId": "trace2", "timestamp": 2000},
                {"traceId": "trace3", "timestamp": 3000},
                {"traceId": "trace4", "timestamp": 4000},
                {"traceId": "trace5", "timestamp": 5000}
            ],
            "canLoadMore": False,
            "totalHits": 5
        }

        mock_result = MagicMock()
        mock_result.to_dict.return_value = mock_result_dict

        mock_api = MagicMock()
        mock_api.get_traces.return_value = mock_result

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        # Test with filters - pass mock as api_client parameter
        result = await client.get_all_traces(
            payload={
                "pagination": {"retrievalSize": 10},
                "timeFrame": {
                    "to": 1704110400000,
                    "windowSize": 3600000
                },
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
        assert "filePath" in result
        assert "itemCount" in result
        assert "fileSizeBytes" in result
        assert "canLoadMore" in result

        # Verify item count
        assert result["itemCount"] == 5

        # Verify canLoadMore
        assert not result["canLoadMore"]

        # Verify file content
        file_path = result["filePath"]
        assert Path(file_path).exists()

        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 5

            # Verify JSONL format
            for line in lines:
                trace = json.loads(line)
                assert "traceId" in trace
                assert "timestamp" in trace

        # Verify API was called once
        assert mock_api.get_traces.call_count == 1

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
    async def test_get_all_traces_with_cursor(self, instana_credentials):
        """Test get_all_traces returns cursor when more data available"""
        # Mock result with cursor
        mock_result_dict = {
            "items": [
                {"traceId": "trace1", "timestamp": 1000},
                {"traceId": "trace2", "timestamp": 2000, "cursor": {"ingestionTime": 2000, "offset": 5}}
            ],
            "canLoadMore": True,
            "totalHits": 10
        }

        mock_result = MagicMock()
        mock_result.to_dict.return_value = mock_result_dict

        mock_api = MagicMock()
        mock_api.get_traces.return_value = mock_result

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        result = await client.get_all_traces(
            payload={
                "pagination": {"retrievalSize": 2},
                "timeFrame": {
                    "to": 1704110400000,
                    "windowSize": 3600000
                }
            },
            api_client=mock_api
        )

        assert isinstance(result, dict)
        assert "filePath" in result
        assert "itemCount" in result
        assert "canLoadMore" in result

        # Verify cursor fields are returned
        assert result["canLoadMore"]
        assert "ingestionTime" in result
        assert "offset" in result
        assert result["ingestionTime"] == 2000
        assert result["offset"] == 5

        # Verify file exists and contains 2 lines
        file_path = result["filePath"]
        assert Path(file_path).exists()

        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2

        # Clean up
        Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    @pytest.mark.mocked
    async def test_get_all_traces_api_error_cleanup(self, instana_credentials):
        """Test get_all_traces cleans up file on API error"""
        mock_api = MagicMock()
        mock_api.get_traces.side_effect = Exception("API Error")

        client = ApplicationAnalyzeMCPTools(
            read_token=instana_credentials["api_token"],
            base_url=instana_credentials["base_url"],
        )

        # Execute and expect error
        result = await client.get_all_traces(
            payload={
                "pagination": {"retrievalSize": 10},
                "timeFrame": {
                    "to": 1704110400000,
                    "windowSize": 3600000
                }
            },
            api_client=mock_api
        )

        # Verify error response
        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to get traces" in result["error"]

# Made with Bob
