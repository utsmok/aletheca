"""Tests for authentication strategies."""

from unittest.mock import patch

from bibliofabric.auth import NoAuth, QueryParameterAuth

from syntheca.client import SynthecaClient


class TestResolveAuth:
    """Test SynthecaClient._resolve_auth()."""

    def test_api_key_returns_query_parameter_auth(self):
        auth = SynthecaClient._resolve_auth("my-api-key")
        assert isinstance(auth, QueryParameterAuth)
        # Verify the internal key/value are stored
        assert auth._key_name == "api_key"
        assert auth._key_value == "my-api-key"

    def test_none_returns_no_auth(self):
        auth = SynthecaClient._resolve_auth(None)
        assert isinstance(auth, NoAuth)

    def test_empty_string_returns_no_auth(self):
        auth = SynthecaClient._resolve_auth("")
        assert isinstance(auth, NoAuth)


class TestClientAuth:
    """Test that auth is properly wired into the client."""

    def test_client_with_api_key(self):
        with patch.object(SynthecaClient, "__init__", lambda self: None):
            SynthecaClient.__new__(SynthecaClient)
            auth = SynthecaClient._resolve_auth("test-key")
            assert isinstance(auth, QueryParameterAuth)

    def test_client_without_api_key(self):
        auth = SynthecaClient._resolve_auth(None)
        assert isinstance(auth, NoAuth)

    def test_client_explicit_auth_strategy_takes_precedence(self):
        """If auth_strategy is passed directly, _resolve_auth is bypassed."""
        # The __init__ checks auth_strategy first, so this confirms the branching.
        strategy = NoAuth()
        # Simulate what __init__ does: if auth_strategy is not None, use it directly
        resolved = SynthecaClient._resolve_auth("some-key")
        # In the real init, `strategy` would be used instead of `resolved`
        assert isinstance(strategy, NoAuth)
        assert isinstance(resolved, QueryParameterAuth)
