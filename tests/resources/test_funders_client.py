"""Tests for FundersClient."""

import pytest

from syntheca.models import ApiResponse, Funder
from syntheca.resources.funders_client import FundersClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_FUNDER = {
    "id": "https://openalex.org/F123",
    "display_name": "Test Funder",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_FUNDER],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_FUNDER, "id": "https://openalex.org/F1", "display_name": "Funder 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_FUNDER, "id": "https://openalex.org/F2", "display_name": "Funder 2"},
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def funders_client(mock_api_client):
    return FundersClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_funder(funders_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_FUNDER)

    result = await funders_client.get("F123")

    assert isinstance(result, Funder)
    assert result.id == "https://openalex.org/F123"
    assert result.display_name == "Test Funder"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "funders/F123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_funders_no_filters(funders_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await funders_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Funder)
    assert result.results[0].id == "https://openalex.org/F123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_funders(funders_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for funder in funders_client.iterate():
        results.append(funder)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(f, Funder) for f in results)
    assert results[0].id == "https://openalex.org/F1"
    assert results[1].id == "https://openalex.org/F2"
    assert mock_api_client.request.await_count == 2
