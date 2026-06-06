"""Shared test fixtures for syntheca tests."""

import pytest

from syntheca.unwrapper import OpenAlexUnwrapper


@pytest.fixture
def unwrapper():
    return OpenAlexUnwrapper()


@pytest.fixture
def sample_work_json():
    return {
        "id": "https://openalex.org/W1234567890",
        "display_name": "Test Work",
        "title": "A Test Paper",
        "publication_year": 2024,
        "publication_date": "2024-01-15",
        "doi": "https://doi.org/10.1234/test",
        "type": "article",
        "cited_by_count": 42,
        "ids": {"openalex": "W1234567890", "doi": "10.1234/test"},
        "open_access": {
            "is_oa": True,
            "oa_status": "gold",
            "oa_url": "https://example.com/paper",
            "any_repository_has_fulltext": True,
        },
    }


@pytest.fixture
def sample_works_response():
    return {
        "meta": {
            "count": 1,
            "db_response_time_ms": 12.3,
            "page": 1,
            "per_page": 25,
            "next_cursor": "cursor123",
        },
        "results": [
            {
                "id": "https://openalex.org/W1234567890",
                "display_name": "Test Work",
                "title": "A Test Paper",
                "publication_year": 2024,
                "publication_date": "2024-01-15",
                "doi": "https://doi.org/10.1234/test",
                "type": "article",
                "cited_by_count": 42,
                "ids": {"openalex": "W1234567890", "doi": "10.1234/test"},
                "open_access": {
                    "is_oa": True,
                    "oa_status": "gold",
                    "oa_url": "https://example.com/paper",
                    "any_repository_has_fulltext": True,
                },
            }
        ],
    }
