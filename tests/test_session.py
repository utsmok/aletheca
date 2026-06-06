"""Tests for SynthecaSession."""

import pytest

from syntheca.client import SynthecaClient
from syntheca.config import SynthecaSettings
from syntheca.session import SynthecaSession, _QueryAccessor


@pytest.mark.asyncio
async def test_session_context_manager():
    """SynthecaSession works as an async context manager and closes on exit."""
    async with SynthecaSession() as s:
        assert s._api_client is not None
        assert isinstance(s._api_client, SynthecaClient)
        # Client is not closed while inside context
        assert not s._api_client._http_client.is_closed

    # After exit the underlying HTTP client should be closed
    assert s._api_client._http_client.is_closed


@pytest.mark.asyncio
async def test_session_with_api_key():
    """SynthecaSession(api_key=...) should use QueryParameterAuth."""
    async with SynthecaSession(api_key="test-key") as s:
        auth = s._api_client._auth_strategy
        assert auth.__class__.__name__ == "QueryParameterAuth"
        assert auth._key_name == "api_key"
        assert auth._key_value == "test-key"


@pytest.mark.asyncio
async def test_session_without_api_key_uses_no_auth():
    """SynthecaSession without api_key should default to NoAuth."""
    async with SynthecaSession() as s:
        auth = s._api_client._auth_strategy
        assert auth.__class__.__name__ == "NoAuth"


@pytest.mark.asyncio
async def test_session_delegates_to_client():
    """session.works etc. should delegate to the underlying client via __getattr__."""
    async with SynthecaSession() as s:
        # Accessing a delegated name returns the client's property value
        works_client = s.works
        assert works_client is s._api_client.works

        authors_client = s.authors
        assert authors_client is s._api_client.authors

        # Accessing an unknown attribute raises AttributeError
        with pytest.raises(AttributeError, match="SynthecaSession"):
            _ = s.nonexistent_attr


@pytest.mark.asyncio
async def test_session_queries_accessor():
    """session.queries should return a _QueryAccessor."""
    async with SynthecaSession() as s:
        qa = s.queries
        assert isinstance(qa, _QueryAccessor)
        assert qa._session is s


@pytest.mark.asyncio
async def test_session_custom_settings():
    """SynthecaSession(settings=...) should use those settings."""
    custom = SynthecaSettings(user_agent="test-agent/1.0")
    async with SynthecaSession(settings=custom) as s:
        assert s._settings is custom
        assert s._settings.user_agent == "test-agent/1.0"
        assert s._api_client._settings is custom
