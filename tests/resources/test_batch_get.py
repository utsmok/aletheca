"""Tests for batch_get and auto-generated batch_get_by_* methods."""

import pytest

from aletheca.resources.works_client import WorksClient
from aletheca.resources.authors_client import AuthorsClient
from aletheca.resources.institutions_client import InstitutionsClient
from aletheca.resources.sources_client import SourcesClient
from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

WORK_A = {
    "id": "https://openalex.org/W111",
    "display_name": "Work A",
    "title": "Alpha",
    "publication_year": 2024,
    "type": "article",
    "doi": "https://doi.org/10.1234/alpha",
}
WORK_B = {
    "id": "https://openalex.org/W222",
    "display_name": "Work B",
    "title": "Beta",
    "publication_year": 2023,
    "type": "preprint",
    "doi": "https://doi.org/10.5678/beta",
}
WORK_C = {
    "id": "https://openalex.org/W333",
    "display_name": "Work C",
    "title": "Gamma",
    "publication_year": 2024,
    "type": "article",
    "doi": "https://doi.org/10.9999/gamma",
}

AUTHOR_X = {
    "id": "https://openalex.org/A111",
    "display_name": "Alice",
    "orcid": "https://orcid.org/0000-0001-2345-6789",
}
AUTHOR_Y = {
    "id": "https://openalex.org/A222",
    "display_name": "Bob",
    "orcid": "https://orcid.org/0000-0002-3456-7890",
}
INST_UT = {
    "id": "https://openalex.org/I94624287",
    "display_name": "University of Twente",
    "ror": "https://ror.org/006hf6244",
}
INST_MIT = {
    "id": "https://openalex.org/I85275346",
    "display_name": "MIT",
    "ror": "https://ror.org/042nb2s44",
}
SOURCE_1 = {
    "id": "https://openalex.org/S111",
    "display_name": "Nature",
    "issn": ["1234-5678"],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def works_client(mock_api_client):
    return WorksClient(mock_api_client)


@pytest.fixture
def authors_client(mock_api_client):
    return AuthorsClient(mock_api_client)


@pytest.fixture
def institutions_client(mock_api_client):
    return InstitutionsClient(mock_api_client)


@pytest.fixture
def sources_client(mock_api_client):
    return SourcesClient(mock_api_client)


# ---------------------------------------------------------------------------
# __init_subclass__ auto-generation
# ---------------------------------------------------------------------------


def test_works_client_has_batch_get_by_doi():
    assert hasattr(WorksClient, "batch_get_by_doi")
    assert hasattr(WorksClient, "batch_get_by_openalex_id")
    assert hasattr(WorksClient, "batch_get_by_pmid")
    assert hasattr(WorksClient, "batch_get_by_pmcid")


def test_authors_client_has_batch_get_by_orcid():
    assert hasattr(AuthorsClient, "batch_get_by_orcid")
    assert hasattr(AuthorsClient, "batch_get_by_openalex_id")


def test_institutions_client_has_batch_get_by_ror():
    assert hasattr(InstitutionsClient, "batch_get_by_ror")
    assert hasattr(InstitutionsClient, "batch_get_by_openalex_id")


def test_sources_client_has_batch_get_by_issn():
    assert hasattr(SourcesClient, "batch_get_by_issn")
    assert hasattr(SourcesClient, "batch_get_by_openalex_id")


# ---------------------------------------------------------------------------
# batch_get — core functionality
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_get_empty_input(works_client):
    result = await works_client.batch_get([])
    assert result == {}


@pytest.mark.asyncio
async def test_batch_get_single_batch(works_client, mock_api_client):
    """Single batch (≤50 items) → one search call."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 2}, "results": [WORK_A, WORK_B]}
    )

    result = await works_client.batch_get_by_doi(
        ["10.1234/alpha", "10.5678/beta"]
    )

    assert len(result) == 2
    # Keys are normalized bare DOIs
    assert "10.1234/alpha" in result
    assert "10.5678/beta" in result
    mock_api_client.request.assert_awaited_once()

    # Verify the filter param uses pipe syntax
    call_params = mock_api_client.request.call_args[1].get("params") or mock_api_client.request.call_args.kwargs.get("params")
    assert "10.1234/alpha|10.5678/beta" in call_params.get("filter", "")


@pytest.mark.asyncio
async def test_batch_get_partial_results(works_client, mock_api_client):
    """Only some DOIs found — missing ones absent from result."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 1}, "results": [WORK_A]}
    )

    result = await works_client.batch_get_by_doi(
        ["10.1234/alpha", "10.5678/does_not_exist"]
    )

    assert len(result) == 1
    assert "10.1234/alpha" in result
    assert "10.5678/does_not_exist" not in result


@pytest.mark.asyncio
async def test_batch_get_multiple_batches(works_client, mock_api_client):
    """More than batch_size identifiers → multiple search calls."""
    # Use batch_size=2 to force 2 batches for 3 items
    dois = ["10.1/a", "10.2/b", "10.3/c"]
    mock_api_client.request.side_effect = [
        _mock_response({"meta": {"count": 2}, "results": [WORK_A, WORK_B]}),
        _mock_response({"meta": {"count": 1}, "results": [WORK_C]}),
    ]

    result = await works_client.batch_get_by_doi(dois, batch_size=2)

    assert len(result) == 3
    assert mock_api_client.request.await_count == 2


@pytest.mark.asyncio
async def test_batch_get_no_results(works_client, mock_api_client):
    """All identifiers missing → empty dict."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 0}, "results": []}
    )

    result = await works_client.batch_get_by_doi(["10.0/phantom"])
    assert result == {}


# ---------------------------------------------------------------------------
# Key normalization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_get_doi_normalizes_url_prefix(works_client, mock_api_client):
    """API returns full DOI URLs, keys should be bare DOIs."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 1}, "results": [WORK_A]}
    )

    result = await works_client.batch_get_by_doi(["10.1234/alpha"])

    # Key should be bare DOI, not full URL
    assert "10.1234/alpha" in result
    assert "https://doi.org/10.1234/alpha" not in result


@pytest.mark.asyncio
async def test_batch_get_openalex_id_normalizes(works_client, mock_api_client):
    """API returns full OpenAlex URLs, keys should be bare IDs."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 2}, "results": [WORK_A, WORK_B]}
    )

    result = await works_client.batch_get_by_openalex_id(["W111", "W222"])

    assert "w111" in result
    assert "w222" in result


@pytest.mark.asyncio
async def test_batch_get_by_orcid(authors_client, mock_api_client):
    """ORCID normalization: strip https://orcid.org/ prefix."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 2}, "results": [AUTHOR_X, AUTHOR_Y]}
    )

    result = await authors_client.batch_get_by_orcid(
        ["0000-0001-2345-6789", "0000-0002-3456-7890"]
    )

    assert "0000-0001-2345-6789" in result
    assert "0000-0002-3456-7890" in result


@pytest.mark.asyncio
async def test_batch_get_by_ror(institutions_client, mock_api_client):
    """ROR normalization: strip https://ror.org/ prefix."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 2}, "results": [INST_UT, INST_MIT]}
    )

    result = await institutions_client.batch_get_by_ror(
        ["006hf6244", "042nb2s44"]
    )

    assert "006hf6244" in result
    assert "042nb2s44" in result


@pytest.mark.asyncio
async def test_batch_get_by_issn(sources_client, mock_api_client):
    """ISSN: no URL prefix to strip."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 1}, "results": [SOURCE_1]}
    )

    result = await sources_client.batch_get_by_issn(["1234-5678"])

    assert "1234-5678" in result


# ---------------------------------------------------------------------------
# Generic batch_get with custom field
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_get_custom_field(works_client, mock_api_client):
    """Custom field name passed through correctly."""
    mock_api_client.request.return_value = _mock_response(
        {"meta": {"count": 1}, "results": [WORK_A]}
    )

    result = await works_client.batch_get(
        ["12345"], field="pmid"
    )

    call_params = mock_api_client.request.call_args[1].get("params") or mock_api_client.request.call_args.kwargs.get("params")
    assert call_params.get("filter") == "pmid:12345"
