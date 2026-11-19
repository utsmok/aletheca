"""OpenAlex implementation of bibliofabric's ``ResponseUnwrapper`` protocol.

OpenAlex envelopes look like ``{"meta": {...}, "results": [...]}``; the
``group_by`` endpoint puts typed buckets under a top-level ``group_by`` key
instead of ``results``.
"""

from typing import Any


class OpenAlexUnwrapper:
    """Extracts results, totals, cursors, and metadata from OpenAlex JSON."""

    def results(self, body: Any) -> list[dict[str, Any]]:
        """Return the list of result records in a list/search response."""
        if not isinstance(body, dict):
            return []
        return body.get("results") or []

    def item(self, body: Any) -> dict[str, Any]:
        """Return the record itself; OpenAlex single routes are unwrapped."""
        return body

    def total(self, body: Any) -> int | None:
        """Return ``meta.count``, or ``None`` when absent."""
        count = self._meta(body).get("count")
        return None if count is None else int(count)

    def next_cursor(self, body: Any) -> str | None:
        """Return ``meta.next_cursor``, or ``None`` on the last page."""
        cursor = self._meta(body).get("next_cursor")
        return None if cursor is None else str(cursor)

    def meta(self, body: Any) -> dict[str, Any]:
        """Return the envelope minus ``results`` for :attr:`Page.meta`.

        The ``meta`` dict is flattened to the top level (so ``count``,
        ``cost_usd``, ``x_query``, and ``notice`` read directly), and other
        envelope keys such as ``group_by`` buckets are preserved.
        """
        if not isinstance(body, dict):
            return {}
        merged = {
            key: value for key, value in body.items() if key not in ("meta", "results")
        }
        merged.update(self._meta(body))
        return merged

    @staticmethod
    def _meta(body: Any) -> dict[str, Any]:
        meta = body.get("meta") if isinstance(body, dict) else None
        return meta if isinstance(meta, dict) else {}
