"""Tests for KeywordsClient."""

import pytest

from syntheca.models import ApiResponse, Keyword
from syntheca.resources.keywords_client import KeywordsClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_KEYWORD = {
    "id": "https://openalex.org/K123",
    "display_name": "Test Keyword",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_KEYWORD],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_KEYWORD, "id": "https://openalex.org/K1", "display_name": "Keyword 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_KEYWORD, "id": "https://openalex.org/K2", "display_name": "Keyword 2"},
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def keywords_client(mock_api_client):
    return KeywordsClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_keyword(keywords_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_KEYWORD)

    result = await keywords_client.get("K123")

    assert isinstance(result, Keyword)
    assert result.id == "https://openalex.org/K123"
    assert result.display_name == "Test Keyword"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "keywords/K123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_keywords_no_filters(keywords_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await keywords_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Keyword)
    assert result.results[0].id == "https://openalex.org/K123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_keywords(keywords_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for keyword in keywords_client.iterate():
        results.append(keyword)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(k, Keyword) for k in results)
    assert results[0].id == "https://openalex.org/K1"
    assert results[1].id == "https://openalex.org/K2"
    assert mock_api_client.request.await_count == 2
