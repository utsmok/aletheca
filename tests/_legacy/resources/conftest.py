"""Shared fixtures for resource client tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from aletheca.unwrapper import OpenAlexUnwrapper


def _mock_response(json_data, status_code=200):
    """Build a mock httpx.Response-like object.

    json() is synchronous on real httpx.Response, so use MagicMock (not AsyncMock).
    """
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


@pytest.fixture
def mock_api_client():
    """AsyncMock of AlethecaClient with a mock request method and unwrapper."""
    client = AsyncMock()
    client._response_unwrapper = OpenAlexUnwrapper()
    return client
