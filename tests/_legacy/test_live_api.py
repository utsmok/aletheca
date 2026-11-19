"""Live API smoke tests — run with: uv run pytest tests/test_live_api.py -m live_api

These tests hit the real OpenAlex API and are skipped by default in CI.
"""

import pytest

from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

pytestmark = pytest.mark.live_api


@pytest.fixture
async def session():
    async with AlethecaSession() as s:
        yield s


@pytest.mark.asyncio
async def test_get_work(session):
    work = await session.works.get("W2741809807")
    assert work is not None
    assert work.id is not None
    assert work.display_name is not None


@pytest.mark.asyncio
async def test_get_author(session):
    author = await session.authors.get("A5023888391")
    assert author is not None
    assert author.id is not None


@pytest.mark.asyncio
async def test_get_source(session):
    source = await session.sources.get("S137773608")
    assert source is not None


@pytest.mark.asyncio
async def test_get_institution(session):
    inst = await session.institutions.get("I136233082")
    assert inst is not None


@pytest.mark.asyncio
async def test_get_topic(session):
    topic = await session.topics.get("T10100")
    assert topic is not None


@pytest.mark.asyncio
async def test_get_publisher(session):
    publisher = await session.publishers.get("P4310320990")
    assert publisher is not None


@pytest.mark.asyncio
async def test_get_funder(session):
    funder = await session.funders.get("F4320306100")
    assert funder is not None


@pytest.mark.asyncio
async def test_search_works(session):
    results = await session.works.search(search="machine learning", per_page=3)
    assert results is not None
    assert results.meta.count > 0
    assert len(results.results) > 0


@pytest.mark.asyncio
async def test_filter_works(session):
    filters = WorksFilters(publication_year=2024, is_oa=True)
    results = await session.works.search(filters=filters, per_page=3)
    assert results is not None
    assert results.meta.count > 0


@pytest.mark.asyncio
async def test_works_iterate(session):
    count = 0
    async for _work in session.works.iterate(per_page=3, page_size=3):
        count += 1
        if count >= 3:
            break
    assert count == 3
