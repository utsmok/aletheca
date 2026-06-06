"""OpenAlex-specific response unwrapper implementation.

Handles the OpenAlex JSON response structure:
{
    "meta": {"count": 1000, "next_cursor": "abc123", ...},
    "results": [{...}, {...}]
}
"""

from typing import Any

from bibliofabric.models import ResponseUnwrapper


class OpenAlexUnwrapper(ResponseUnwrapper):
    """OpenAlex implementation of the ResponseUnwrapper protocol."""

    def unwrap_results(self, response_json: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract the list of results from an OpenAlex API response."""
        return response_json.get("results", [])

    def unwrap_single_item(self, response_json: dict[str, Any]) -> dict[str, Any]:
        """Extract a single item. OpenAlex GET /{entity}/{id} returns the entity directly."""
        return response_json

    def get_next_page_token(self, response_json: dict[str, Any]) -> str | None:
        """Extract the next cursor from meta.next_cursor."""
        meta = response_json.get("meta", {})
        if isinstance(meta, dict):
            return meta.get("next_cursor")
        return None

    def get_total_results(self, response_json: dict[str, Any]) -> int | None:
        """Extract the total count from meta.count."""
        meta = response_json.get("meta", {})
        if isinstance(meta, dict):
            count = meta.get("count")
            if count is not None:
                return int(count)
        return None
