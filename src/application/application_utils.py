"""
Application layer utilities for Instana MCP
Provides generic pagination handling for Application APIs
"""
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PagerResult(BaseModel):
    """Result of pagination operation"""
    file_path: str
    item_count: int
    file_size_bytes: int
    stop_reason: str  # "all_fetched" | "limit_reached"


def paginate_and_collect(
    fetcher: Callable[[Optional[Any]], Dict[str, Any]],
    output_path: str,
    max_retrieval_size: int = 200
) -> PagerResult:
    """
    Generic pagination handler for Instana Application APIs

    Assumptions:
    - fetcher returns {"items": [...], "canLoadMore": bool}
    - Each item in items contains a "cursor" field
    - Items are written to output_path in JSONL format

    Args:
        fetcher: Page fetcher function (cursor) -> Dict
        output_path: Output file path for JSONL data
        max_retrieval_size: Maximum number of items to collect

    Returns:
        PagerResult with collection statistics
    """
    total_items = 0
    cursor = None
    stop_reason = "all_fetched"

    try:
        while total_items < max_retrieval_size:
            result = fetcher(cursor)
            items = result.get("items", [])

            if not items:
                break

            # Write items to JSONL file
            with open(output_path, 'a') as f:
                for item in items:
                    f.write(json.dumps(item) + '\n')

            total_items += len(items)

            # Then check limit
            if total_items >= max_retrieval_size:
                stop_reason = "limit_reached"
                break

            # Check if more pages available
            if not result.get("canLoadMore", False):
                break

            # Update cursor for next page
            if items and "cursor" in items[-1]:
                cursor = items[-1]["cursor"]

        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

        return PagerResult(
            file_path=output_path,
            item_count=total_items,
            file_size_bytes=file_size,
            stop_reason=stop_reason
        )

    except Exception as e:
        logger.error(f"Pagination failed: {e}", exc_info=True)
        if Path(output_path).exists():
            Path(output_path).unlink()
        raise

# Made with Bob
