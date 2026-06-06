"""Tests for PublishersClient."""

import pytest

from syntheca.models import ApiResponse, Publisher
from syntheca.resources.publishers_client import PublishersClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_PUBLISHER = {
    "id": "https://openalex.org/P123",
    "display_name": "Test Publisher",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_PUBLISHER],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {
            **MINIMAL_PUBLISHER,
            "id": "https://openalex.org/P1",
            "display_name": "Publisher 1",
        },
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {
            **MINIMAL_PUBLISHER,
            "id": "https://openalex.org/P2",
            "display_name": "Publisher 2",
        },
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def publishers_client(mock_api_client):
    return PublishersClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_publisher(publishers_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_PUBLISHER)

    result = await publishers_client.get("P123")

    assert isinstance(result, Publisher)
    assert result.id == "https://openalex.org/P123"
    assert result.display_name == "Test Publisher"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "publishers/P123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_publishers_no_filters(publishers_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await publishers_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Publisher)
    assert result.results[0].id == "https://openalex.org/P123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_publishers(publishers_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for publisher in publishers_client.iterate():
        results.append(publisher)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(p, Publisher) for p in results)
    assert results[0].id == "https://openalex.org/P1"
    assert results[1].id == "https://openalex.org/P2"
    assert mock_api_client.request.await_count == 2
