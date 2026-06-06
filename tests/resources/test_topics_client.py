"""Tests for TopicsClient."""

import pytest

from aletheca.models import ApiResponse, Topic
from aletheca.resources.topics_client import TopicsClient

from .conftest import _mock_response

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

MINIMAL_TOPIC = {
    "id": "https://openalex.org/T123",
    "display_name": "Test Topic",
}

SEARCH_RESPONSE = {
    "meta": {"count": 1, "next_cursor": "cursor_abc"},
    "results": [MINIMAL_TOPIC],
}

PAGE1 = {
    "meta": {"count": 2, "next_cursor": "cursor_page2"},
    "results": [
        {**MINIMAL_TOPIC, "id": "https://openalex.org/T1", "display_name": "Topic 1"},
    ],
}

PAGE2 = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {**MINIMAL_TOPIC, "id": "https://openalex.org/T2", "display_name": "Topic 2"},
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def topics_client(mock_api_client):
    return TopicsClient(mock_api_client)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_topic(topics_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(MINIMAL_TOPIC)

    result = await topics_client.get("T123")

    assert isinstance(result, Topic)
    assert result.id == "https://openalex.org/T123"
    assert result.display_name == "Test Topic"
    mock_api_client.request.assert_awaited_once()
    call_args = mock_api_client.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "topics/T123"


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_topics_no_filters(topics_client, mock_api_client):
    mock_api_client.request.return_value = _mock_response(SEARCH_RESPONSE)

    result = await topics_client.search()

    assert isinstance(result, ApiResponse)
    assert result.meta.count == 1
    assert len(result.results) == 1
    assert isinstance(result.results[0], Topic)
    assert result.results[0].id == "https://openalex.org/T123"


# ---------------------------------------------------------------------------
# iterate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_iterate_topics(topics_client, mock_api_client):
    mock_api_client.request.side_effect = [
        _mock_response(PAGE1),
        _mock_response(PAGE2),
    ]

    results = []
    async for topic in topics_client.iterate():
        results.append(topic)  # noqa: PERF401

    assert len(results) == 2
    assert all(isinstance(t, Topic) for t in results)
    assert results[0].id == "https://openalex.org/T1"
    assert results[1].id == "https://openalex.org/T2"
    assert mock_api_client.request.await_count == 2
