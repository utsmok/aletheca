"""Tests for SourcesClient."""

import pytest

from aletheca.models import ApiResponse, Source
from aletheca.resources.sources_client import SourcesClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_SOURCE = {
    "id": "https://openalex.org/S123",
    "display_name": "Test Source",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_SOURCE],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_SOURCE, "id": "https://openalex.org/S1", "display_name": "Source 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_SOURCE, "id": "https://openalex.org/S2", "display_name": "Source 2"},
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sources_client(mock_api_client):
    return SourcesClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_source(sources_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_SOURCE)

    result = await sources_client.get("S123")

    assert isinstance(result, Source)
    assert result.id == "https://openalex.org/S123"
    assert result.display_name == "Test Source"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "sources/S123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_sources_no_filters(sources_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await sources_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Source)
    assert result.results[0].id == "https://openalex.org/S123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_sources(sources_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for source in sources_client.iterate():
        results.append(source)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(s, Source) for s in results)
    assert results[0].id == "https://openalex.org/S1"
    assert results[1].id == "https://openalex.org/S2"
    assert mock_api_client.request.await_count == 2
