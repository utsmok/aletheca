"""Tests for AlethecaClient."""

import pytest
from bibliofabric.auth import NoAuth, QueryParameterAuth

from aletheca.client import AlethecaClient
from aletheca.resources import (
    AuthorsClient,
    FundersClient,
    InstitutionsClient,
    KeywordsClient,
    PublishersClient,
    SourcesClient,
    TopicsClient,
    WorksClient,
)


@pytest.mark.asyncio
async def test_context_manager_enter_exit():
    """Async context manager should open then close the HTTP client."""
    async with AlethecaClient() as client:
        assert not client._http_client.is_closed
    assert client._http_client.is_closed


def test_no_auth_fallback():
    """Client with no api_key should use NoAuth strategy."""
    client = AlethecaClient()
    assert isinstance(client._auth_strategy, NoAuth)


def test_api_key_auth():
    """Client with api_key should use QueryParameterAuth strategy."""
    client = AlethecaClient(api_key="test-key")
    assert isinstance(client._auth_strategy, QueryParameterAuth)


def test_explicit_auth_strategy_override():
    """Passing auth_strategy should override api_key resolution."""
    client = AlethecaClient(api_key="test-key", auth_strategy=NoAuth())
    assert isinstance(client._auth_strategy, NoAuth)


def test_resource_client_properties():
    """Lazy-loaded resource properties should return correct client types."""
    client = AlethecaClient()
    assert isinstance(client.works, WorksClient)
    assert isinstance(client.authors, AuthorsClient)
    assert isinstance(client.sources, SourcesClient)
    assert isinstance(client.institutions, InstitutionsClient)
    assert isinstance(client.topics, TopicsClient)
    assert isinstance(client.keywords, KeywordsClient)
    assert isinstance(client.publishers, PublishersClient)
    assert isinstance(client.funders, FundersClient)
