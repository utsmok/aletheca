"""Tests for AuthorsClient."""

import pytest

from syntheca.models import ApiResponse, Author
from syntheca.resources.authors_client import AuthorsClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_AUTHOR = {
    "id": "https://openalex.org/A123",
    "display_name": "Test Author",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_AUTHOR],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_AUTHOR, "id": "https://openalex.org/A1", "display_name": "Author 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_AUTHOR, "id": "https://openalex.org/A2", "display_name": "Author 2"},
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def authors_client(mock_api_client):
    return AuthorsClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_author(authors_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_AUTHOR)

    result = await authors_client.get("A123")

    assert isinstance(result, Author)
    assert result.id == "https://openalex.org/A123"
    assert result.display_name == "Test Author"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "authors/A123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_authors_no_filters(authors_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await authors_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Author)
    assert result.results[0].id == "https://openalex.org/A123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_authors(authors_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for author in authors_client.iterate():
        results.append(author)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(a, Author) for a in results)
    assert results[0].id == "https://openalex.org/A1"
    assert results[1].id == "https://openalex.org/A2"
    assert mock_api_client.request.await_count == 2
