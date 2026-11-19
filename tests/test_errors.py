"""Error mapping, the retry veto, and iteration failure handling."""

import pytest

from aletheca import (
    AlethecaClient,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

from .conftest import entity, envelope


def retrying(settings) -> AlethecaClient:
    return AlethecaClient(settings=settings.model_copy(update={"max_retries": 1}))


async def test_404_maps_to_not_found(client, httpx_mock):
    httpx_mock.add_response(status_code=404, json={"error": "not found"})
    with pytest.raises(NotFoundError) as excinfo:
        await client.works.get("Nope")
    assert excinfo.value.body == {"error": "not found"}
    assert "404" in str(excinfo.value)


async def test_429_maps_to_rate_limit_error(client, httpx_mock):
    httpx_mock.add_response(status_code=429, json={})
    with pytest.raises(RateLimitError):
        await client.works.search()


async def test_daily_budget_429_is_not_retried(httpx_mock, settings):
    client = retrying(settings)
    httpx_mock.add_response(status_code=429, json={"reason": "daily_budget"})
    with pytest.raises(RateLimitError) as excinfo:
        await client.works.search()
    assert len(httpx_mock.get_requests()) == 1
    assert excinfo.value.body == {"reason": "daily_budget"}


async def test_other_429_retries(client, httpx_mock, settings):
    client = retrying(settings)
    httpx_mock.add_response(status_code=429, text="slow down")
    httpx_mock.add_response(status_code=429, json={})
    with pytest.raises(RateLimitError):
        await client.works.search()
    assert len(httpx_mock.get_requests()) == 2


async def test_500_retries_then_succeeds(httpx_mock, settings):
    client = retrying(settings)
    httpx_mock.add_response(status_code=500, json={}, headers={"Retry-After": "0"})
    httpx_mock.add_response(json=entity("W1"))
    work = await client.works.get("W1")
    assert work.id == "https://openalex.org/W1"
    assert len(httpx_mock.get_requests()) == 2


async def test_record_validation_failure_maps_to_validation_error(client, httpx_mock):
    httpx_mock.add_response(json=envelope([42], count=1))
    with pytest.raises(ValidationError) as excinfo:
        await client.works.search()
    assert excinfo.value.model_name == "Work"
    assert excinfo.value.raw == 42


async def test_iterate_skip_mode_records_failures(client, httpx_mock):
    good = entity("W1")
    httpx_mock.add_response(json=envelope([42, good]))
    failures: list[tuple[dict, Exception]] = []
    collected = [
        work async for work in client.works.iterate(on_error="skip", failures=failures)
    ]
    assert [work.id for work in collected] == [good["id"]]
    assert len(failures) == 1
