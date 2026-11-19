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


async def test_locations_smoke(live_client):
    record_id = load_fixture("location.json")["id"]
    record = await live_client.locations.get(record_id)
    assert record.id == record_id
    assert record.work_id
    page = await live_client.locations.search({"doi": "10.7717/peerj.4375"})
    assert page.total is not None and page.total > 0


async def test_links_smoke(live_client):
    edges = await live_client.links.origin("W2741809807", limit=10)
    assert edges
    assert edges[0].origin.endswith("W2741809807")
    assert edges[0].relationship.startswith("https://openalex.org/relationships/")


async def test_rerank_smoke(live_client):
    page = await live_client.works.search(
        query="open peer review", rerank=True, select=["id"]
    )
    assert page.meta.get("reranked") is True


async def test_oa_pdf_urls_smoke(live_client):
    work_id = load_fixture("work_multi_oa.json")["id"].rsplit("/", 1)[-1]
    urls = await live_client.works.oa_pdf_urls(work_id)
    assert urls
    assert all(url.startswith("http") for url in urls)


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
