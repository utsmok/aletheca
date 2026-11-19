"""Shared fixtures: an AlethecaClient wired through pytest-httpx.

Settings are built with every relevant field explicit (and ``_env_file=None``)
so the suite never depends on the developer's shell or ``.env``.
"""

import json
from pathlib import Path

import pytest

from aletheca import AlethecaClient, AlethecaSettings

BASE_URL = "https://api.openalex.org"
FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a trimmed real-API payload from ``tests/fixtures``."""
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def settings():
    """Fast, deterministic settings: no throttle, no retries."""
    return AlethecaSettings(
        _env_file=None,
        api_key="test-key",
        max_requests_per_second=1_000_000.0,
        max_concurrency=5,
        max_retries=0,
        max_retry_wait=0.05,
        timeout=5.0,
    )


@pytest.fixture
def client(settings):
    return AlethecaClient(settings=settings)


def envelope(results: list, *, count: int = 1, next_cursor: str | None = None) -> dict:
    """Build an OpenAlex list/search envelope."""
    meta: dict = {"count": count}
    if next_cursor is not None:
        meta["next_cursor"] = next_cursor
    return {"meta": meta, "results": results}


def entity(record_id: str) -> dict:
    """Minimal entity record that validates against every entity model."""
    return {"id": f"https://openalex.org/{record_id}", "display_name": record_id}
