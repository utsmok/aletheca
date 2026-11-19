"""Tests for AlethecaSession."""

import pytest

from aletheca.client import AlethecaClient
from aletheca.config import AlethecaSettings
from aletheca.session import AlethecaSession, _QueryAccessor


@pytest.mark.asyncio
async def test_session_context_manager():
    """AlethecaSession works as an async context manager and closes on exit."""
    async with AlethecaSession() as s:
        assert s._api_client is not None
        assert isinstance(s._api_client, AlethecaClient)
        # Client is not closed while inside context
        assert not s._api_client._http_client.is_closed

    # After exit the underlying HTTP client should be closed
    assert s._api_client._http_client.is_closed


@pytest.mark.asyncio
async def test_session_with_api_key():
    """AlethecaSession(api_key=...) should use QueryParameterAuth."""
    async with AlethecaSession(api_key="test-key") as s:
        auth = s._api_client._auth_strategy
        assert auth.__class__.__name__ == "QueryParameterAuth"
        assert auth._key_name == "api_key"
        assert auth._key_value == "test-key"


@pytest.mark.asyncio
async def test_session_without_api_key_uses_no_auth():
    """AlethecaSession without api_key should default to NoAuth."""
    async with AlethecaSession() as s:
        auth = s._api_client._auth_strategy
        assert auth.__class__.__name__ == "NoAuth"


@pytest.mark.asyncio
async def test_session_delegates_to_client():
    """session.works etc. should delegate to the underlying client via __getattr__."""
    async with AlethecaSession() as s:
        # Accessing a delegated name returns the client's property value
        works_client = s.works
        assert works_client is s._api_client.works

        authors_client = s.authors
        assert authors_client is s._api_client.authors

        # Accessing an unknown attribute raises AttributeError
        with pytest.raises(AttributeError, match="AlethecaSession"):
            _ = s.nonexistent_attr


@pytest.mark.asyncio
async def test_session_queries_accessor():
    """session.queries should return a _QueryAccessor."""
    async with AlethecaSession() as s:
        qa = s.queries
        assert isinstance(qa, _QueryAccessor)
        assert qa._session is s


@pytest.mark.asyncio
async def test_session_custom_settings():
    """AlethecaSession(settings=...) should use those settings."""
    custom = AlethecaSettings(user_agent="test-agent/1.0")
    async with AlethecaSession(settings=custom) as s:
        assert s._settings is custom
        assert s._settings.user_agent == "test-agent/1.0"
        assert s._api_client._settings is custom
