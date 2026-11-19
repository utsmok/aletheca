"""Live OpenAlex smoke tests, one per resource.

Deselected by default; run with ``uv run pytest -m live_api`` and
``ALETHECA_API_KEY`` exported. Each test fetches the same real record its
fixture in ``tests/fixtures`` was trimmed from.
"""

import os

import pytest

from aletheca import AlethecaClient, AlethecaSettings

from .conftest import load_fixture

pytestmark = pytest.mark.live_api


@pytest.fixture
def live_client():
    key = os.environ.get("ALETHECA_API_KEY")
    if not key:
        pytest.skip("ALETHECA_API_KEY is not exported")
    settings = AlethecaSettings(_env_file=None, api_key=key)
    return AlethecaClient(settings=settings)


@pytest.mark.parametrize(
    ("resource", "fixture"),
    [
        ("works", "work.json"),
        ("authors", "author.json"),
        ("sources", "source.json"),
        ("institutions", "institution.json"),
        ("topics", "topic.json"),
        ("keywords", "keyword.json"),
        ("publishers", "publisher.json"),
        ("funders", "funder.json"),
        ("awards", "award.json"),
    ],
)
async def test_resource_get_smoke(live_client, resource, fixture):
    record_id = load_fixture(fixture)["id"]
    result = await getattr(live_client, resource).get(record_id)
    assert result.id == record_id


async def test_search_smoke(live_client):
    page = await live_client.works.search({"publication_year": 2024}, select=["id"])
    assert page.total is not None and page.total > 0
    assert page.results[0].id


async def test_count_smoke(live_client):
    assert await live_client.works.count({"is_oa": True}) > 0


async def test_iterate_smoke(live_client):
    collected = [
        work
        async for work in live_client.works.iterate(
            {"publication_year": 2024}, select=["id"], limit=3
        )
    ]
    assert len(collected) == 3


async def test_autocomplete_smoke(live_client):
    rows = await live_client.autocomplete("utrecht")
    assert len(rows) > 0


async def test_rate_limit_smoke(live_client):
    status = await live_client.rate_limit()
    assert status.rate_limit.daily_remaining_usd is not None
