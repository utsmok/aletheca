"""Tests for WorksClient."""

import pytest
from bibliofabric.exceptions import BibliofabricError

from aletheca.endpoints import WorksFilters
from aletheca.models import ApiResponse, Work
from aletheca.resources.works_client import WorksClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

MINIMAL_WORK = {
    "id": "https://openalex.org/W123",
    "display_name": "Test Work",
    "title": "A Test Paper",
    "publication_year": 2024,
    "type": "article",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_WORK],
}

EMPTY_SEARCH_RESPONSE = {
    "meta": {"count": 0, "next_cursor": None},
    "results": [],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_WORK, "id": "https://openalex.org/W1", "display_name": "Work 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_WORK, "id": "https://openalex.org/W2", "display_name": "Work 2"},
    ],
}


@pytest.fixture
def works_client(mock_api_client):
    return WorksClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_work(works_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_WORK)

    result = await works_client.get("W123")

    assert isinstance(result, Work)
    assert result.id == "https://openalex.org/W123"
    assert result.title == "A Test Paper"
    assert result.publication_year == 2024
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "works/W123"


@pytest.mark.asyncio
async def test_get_work_accepts_full_url_id(works_client, mock_api_client):
    """Entity records carry full-URL ids; get() must reduce them to the route key."""
    mock_api_client.request.return_value = _mock_response(MINIMAL_WORK)

    result = await works_client.get("https://openalex.org/W123")

    assert isinstance(result, Work)
    call_args = mock_api_client.request.call_args
    assert call_args[0][1] == "works/W123"


@pytest.mark.asyncio
async def test_get_work_keeps_doi_url(works_client, mock_api_client):
    """DOI URLs are valid direct-get keys and must pass through untouched."""
    mock_api_client.request.return_value = _mock_response(MINIMAL_WORK)

    await works_client.get("https://doi.org/10.1038/nature12373")

    call_args = mock_api_client.request.call_args
    assert call_args[0][1] == "works/https://doi.org/10.1038/nature12373"


@pytest.mark.asyncio
async def test_get_work_wraps_unexpected_error(works_client, mock_api_client):
    """Verify that unexpected errors from request() are wrapped in BibliofabricError."""
    mock_api_client.request.side_effect = Exception("Unexpected error")
    with pytest.raises(BibliofabricError, match="Unexpected error"):
        await works_client.get("W999")


@pytest.mark.asyncio
async def test_get_work_raises_bibliofabric_error_on_404(works_client, mock_api_client):
    """Verify that a 404 API response raises BibliofabricError."""
    from bibliofabric.exceptions import APIError  # noqa: PLC0415

    error = APIError("Not found", response=None)
    mock_api_client.request.side_effect = error
    with pytest.raises(BibliofabricError):
        await works_client.get("W-nonexistent")


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_works_no_filters(works_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await works_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Work)
    assert result.results[0].id == "https://openalex.org/W123"


@pytest.mark.asyncio
async def test_search_works_with_filters(works_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    filters = WorksFilters(publication_year=2024, is_oa=True)
    await works_client.search(filters=filters)

    call_args = mock_api_client.request.call_args
    params = call_args.kwargs.get("params") or call_args[1].get("params")
    assert params is not None
    assert "filter" in params
    # Should contain both filters serialized as key:value
    filter_str = params["filter"]
    assert "publication_year:2024" in filter_str
    assert "is_oa:True" in filter_str


@pytest.mark.asyncio
async def test_search_sort_field_passed_through(works_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    await works_client.search(sort_by="cited_by_count:desc")

    call_args = mock_api_client.request.call_args
    params = call_args.kwargs.get("params") or call_args[1].get("params")
    assert params is not None
    assert params.get("sort") == "cited_by_count:desc"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_works(works_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = [work async for work in works_client.iterate()]

    assert len(results) == 2
    assert all(isinstance(w, Work) for w in results)
    assert results[0].id == "https://openalex.org/W1"
    assert results[1].id == "https://openalex.org/W2"
    # Two pages fetched
    assert mock_api_client.request.await_count == 2


@pytest.mark.asyncio
async def test_iterate_works_no_results(works_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(EMPTY_SEARCH_RESPONSE)

    results = [work async for work in works_client.iterate()]

    assert results == []
    mock_api_client.request.assert_awaited_once()


@pytest.mark.asyncio
async def test_iterate_api_error_during_iteration(works_client, mock_api_client):
    # First page succeeds, second page raises
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        Exception("Internal Server Error"),
    ]

    with pytest.raises(BibliofabricError, match="works"):
        async for _ in works_client.iterate():
            pass

    # Two requests attempted: first page succeeded, second raised
    assert mock_api_client.request.await_count == 2
