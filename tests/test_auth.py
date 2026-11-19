"""Credential wiring: where the API key travels on the wire."""

import pytest
from bibliofabric.auth import NoAuth

from aletheca import AlethecaClient, APIError, AuthError

from .conftest import entity


def keyless(settings) -> AlethecaClient:
    return AlethecaClient(settings=settings.model_copy(update={"api_key": None}))


async def test_default_scheme_sends_api_key_query_param(client, httpx_mock):
    httpx_mock.add_response(json=entity("W1"))
    await client.works.get("W1")
    request = httpx_mock.get_requests()[-1]
    assert request.url.params["api_key"] == "test-key"
    assert "authorization" not in request.headers


async def test_bearer_scheme_sends_authorization_header(settings, httpx_mock):
    client = AlethecaClient(
        settings=settings.model_copy(update={"auth_scheme": "bearer"})
    )
    httpx_mock.add_response(json=entity("W1"))
    await client.works.get("W1")
    request = httpx_mock.get_requests()[-1]
    assert request.headers["authorization"] == "Bearer test-key"
    assert "api_key" not in request.url.params


async def test_keyless_client_sends_no_credential(settings, httpx_mock):
    client = keyless(settings)
    httpx_mock.add_response(json=entity("W1"))
    await client.works.get("W1")
    request = httpx_mock.get_requests()[-1]
    assert "api_key" not in request.url.params
    assert "authorization" not in request.headers


async def test_explicit_strategy_wins_over_key(settings, httpx_mock):
    client = AlethecaClient(
        settings=settings, auth_strategy=NoAuth(), api_key="ignored"
    )
    httpx_mock.add_response(json=entity("W1"))
    await client.works.get("W1")
    request = httpx_mock.get_requests()[-1]
    assert "api_key" not in request.url.params


async def test_keyless_401_gets_actionable_message(settings, httpx_mock):
    httpx_mock.add_response(status_code=401, json={})
    client = keyless(settings)
    with pytest.raises(AuthError) as excinfo:
        await client.works.search()
    message = str(excinfo.value)
    assert "ALETHECA_API_KEY" in message
    assert "api_key=" in message


async def test_keyed_401_keeps_upstream_message(client, httpx_mock):
    httpx_mock.add_response(status_code=401, json={})
    with pytest.raises(AuthError) as excinfo:
        await client.works.search()
    assert "Get a free API key" not in str(excinfo.value)


async def test_error_str_redacts_credential(client, httpx_mock):
    httpx_mock.add_response(status_code=500, json={})
    with pytest.raises(APIError) as excinfo:
        await client.works.search()
    assert "test-key" not in str(excinfo.value)
    assert "test-key" not in excinfo.value.message
