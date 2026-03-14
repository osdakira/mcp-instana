"""
Unit tests for application_utils module.
"""

import json
import tempfile
import unittest
from pathlib import Path

from src.application.application_utils import PagerResult, paginate_and_collect


class TestPaginateAndCollect(unittest.TestCase):
    """Test cases for paginate_and_collect function"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_path = self.temp_dir / "test_output.jsonl"

    def tearDown(self):
        """Clean up test files"""
        if self.output_path.exists():
            self.output_path.unlink()
        self.temp_dir.rmdir()

    def test_paginate_single_page(self):
        """Test pagination with single page"""
        items = [
            {"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}},
            {"id": 2, "cursor": {"ingestionTime": 100, "offset": 1}},
        ]

        def fetcher(cursor):
            return {"items": items, "canLoadMore": False}

        result = paginate_and_collect(
            fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=100
        )

        self.assertEqual(result.item_count, 2)
        self.assertEqual(result.stop_reason, "all_fetched")
        self.assertTrue(Path(result.file_path).exists())

        # Verify file content
        with Path(result.file_path).open("r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["id"], 1)
            self.assertEqual(json.loads(lines[1])["id"], 2)

    def test_paginate_multiple_pages(self):
        """Test pagination with multiple pages"""
        page1 = [
            {"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}},
            {"id": 2, "cursor": {"ingestionTime": 100, "offset": 1}},
        ]
        page2 = [
            {"id": 3, "cursor": {"ingestionTime": 100, "offset": 2}},
            {"id": 4, "cursor": {"ingestionTime": 100, "offset": 3}},
        ]

        call_count = [0]

        def fetcher(cursor):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"items": page1, "canLoadMore": True}
            else:
                return {"items": page2, "canLoadMore": False}

        result = paginate_and_collect(
            fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=100
        )

        self.assertEqual(result.item_count, 4)
        self.assertEqual(result.stop_reason, "all_fetched")

        # Verify file content
        with Path(result.file_path).open("r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 4)

    def test_paginate_with_max_retrieval_size_limit(self):
        """Test pagination stops at max_retrieval_size"""
        items = [
            {"id": i, "cursor": {"ingestionTime": 100, "offset": i}}
            for i in range(10)
        ]

        def fetcher(cursor):
            return {"items": items, "canLoadMore": True}

        result = paginate_and_collect(
            fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=5
        )

        self.assertEqual(result.item_count, 10)  # First call returns 10 items
        self.assertEqual(result.stop_reason, "limit_reached")

    def test_paginate_empty_response(self):
        """Test pagination with empty response"""

        def fetcher(cursor):
            return {"items": [], "canLoadMore": False}

        result = paginate_and_collect(
            fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=100
        )

        self.assertEqual(result.item_count, 0)
        self.assertEqual(result.stop_reason, "all_fetched")

    def test_paginate_cursor_propagation(self):
        """Test that cursor is properly propagated between pages"""
        cursors_received = []

        def fetcher(cursor):
            cursors_received.append(cursor)
            if cursor is None:
                return {
                    "items": [{"id": 1, "cursor": {"ingestionTime": 100, "offset": 0}}],
                    "canLoadMore": True,
                }
            else:
                return {"items": [], "canLoadMore": False}

        paginate_and_collect(
            fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=100
        )

        self.assertEqual(len(cursors_received), 2)
        self.assertIsNone(cursors_received[0])
        self.assertEqual(cursors_received[1], {"ingestionTime": 100, "offset": 0})

    def test_paginate_error_handling(self):
        """Test error handling during pagination"""

        def fetcher(cursor):
            raise Exception("API error")

        with self.assertRaises(Exception) as context:
            paginate_and_collect(
                fetcher=fetcher, output_path=str(self.output_path), max_retrieval_size=100
            )

        self.assertIn("API error", str(context.exception))
        # Verify file is cleaned up on error
        self.assertFalse(self.output_path.exists())

    def test_pager_result_model(self):
        """Test PagerResult model"""
        result = PagerResult(
            file_path="/tmp/test.jsonl",
            item_count=10,
            file_size_bytes=1024,
            stop_reason="all_fetched",
        )

        self.assertEqual(result.file_path, "/tmp/test.jsonl")
        self.assertEqual(result.item_count, 10)
        self.assertEqual(result.file_size_bytes, 1024)
        self.assertEqual(result.stop_reason, "all_fetched")


if __name__ == "__main__":
    unittest.main()

# Made with Bob
