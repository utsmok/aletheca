"""Tests for InstitutionsClient."""

import pytest

from aletheca.models import ApiResponse, Institution
from aletheca.resources.institutions_client import InstitutionsClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_INSTITUTION = {
    "id": "https://openalex.org/I123",
    "display_name": "Test Institution",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_INSTITUTION],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {
            **MINIMAL_INSTITUTION,
            "id": "https://openalex.org/I1",
            "display_name": "Institution 1",
        },
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {
            **MINIMAL_INSTITUTION,
            "id": "https://openalex.org/I2",
            "display_name": "Institution 2",
        },
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def institutions_client(mock_api_client):
    return InstitutionsClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_institution(institutions_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_INSTITUTION)

    result = await institutions_client.get("I123")

    assert isinstance(result, Institution)
    assert result.id == "https://openalex.org/I123"
    assert result.display_name == "Test Institution"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "institutions/I123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_institutions_no_filters(institutions_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await institutions_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Institution)
    assert result.results[0].id == "https://openalex.org/I123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_institutions(institutions_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for institution in institutions_client.iterate():
        results.append(institution)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(i, Institution) for i in results)
    assert results[0].id == "https://openalex.org/I1"
    assert results[1].id == "https://openalex.org/I2"
    assert mock_api_client.request.await_count == 2
