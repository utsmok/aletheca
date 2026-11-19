"""Parsing of real OpenAlex payloads into the typed models."""

import pytest

from aletheca import GroupByBucket

from .conftest import load_fixture


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
async def test_single_entity_parses_from_real_payload(
    client, httpx_mock, resource, fixture
):
    payload = load_fixture(fixture)
    entity_id = payload["id"].rsplit("/", 1)[-1]
    httpx_mock.add_response(json=payload)
    result = await getattr(client, resource).get(entity_id)
    assert result.id == payload["id"]
    assert result.display_name == payload["display_name"]


async def test_work_parses_drift_fixed_fields(client, httpx_mock):
    payload = load_fixture("work.json")
    httpx_mock.add_response(json=payload)
    work = await client.works.get(payload["id"])
    assert work.title == payload["title"]
    assert work.doi == payload["doi"]
    assert work.is_traditional is True
    assert work.child_works_count == payload["child_works_count"]
    assert work.referenced_works_count == payload["referenced_works_count"]
    assert work.content_urls is not None
    assert work.content_urls.pdf == payload["content_urls"]["pdf"]
    assert work.lineage[0] == payload["lineage"][0]
    assert work.authorships[0].author.id == payload["authorships"][0]["author"]["id"]
    assert work.abstract_inverted_index is not None
    assert isinstance(work.reconstructed_abstract, str)
    assert len(work.reconstructed_abstract.split()) > 5


async def test_funder_parses_awards_not_grants(client, httpx_mock):
    payload = load_fixture("funder.json")
    funder_id = payload["id"].rsplit("/", 1)[-1]
    httpx_mock.add_response(json=payload)
    funder = await client.funders.get(funder_id)
    assert funder.awards_count == payload["awards_count"]
    assert not hasattr(funder, "grants_count")


async def test_award_parses_institution_awarded_list(client, httpx_mock):
    payload = load_fixture("award.json")
    award_id = payload["id"].rsplit("/", 1)[-1]
    httpx_mock.add_response(json=payload)
    award = await client.awards.get(award_id)
    assert isinstance(award.institution_awarded, list)


async def test_institution_parses_status_and_repositories(client, httpx_mock):
    payload = load_fixture("institution.json")
    institution_id = payload["id"].rsplit("/", 1)[-1]
    httpx_mock.add_response(json=payload)
    institution = await client.institutions.get(institution_id)
    assert institution.status == payload["status"]
    assert isinstance(institution.repositories, list)


async def test_author_parses_live_only_fields(client, httpx_mock):
    payload = load_fixture("author.json")
    author_id = payload["id"].rsplit("/", 1)[-1]
    httpx_mock.add_response(json=payload)
    author = await client.authors.get(author_id)
    assert author.full_name == payload["full_name"]
    assert author.block_key == payload["block_key"]
    assert author.awards_count == payload["awards_count"]


async def test_search_parses_page_envelope(client, httpx_mock):
    work = load_fixture("work.json")
    body = {
        "meta": {
            "count": 1,
            "next_cursor": "I100",
            "per_page": 25,
            "cost_usd": 0.0001,
        },
        "results": [work],
    }
    httpx_mock.add_response(json=body)
    page = await client.works.search(query="open access")
    assert page.total == 1
    assert page.next_cursor == "I100"
    assert page.results[0].id == work["id"]
    assert page.meta["cost_usd"] == 0.0001
    assert page.meta["per_page"] == 25


async def test_group_by_buckets_parse_nested_groups(client, httpx_mock):
    buckets = load_fixture("group_by.json")["group_by"]
    httpx_mock.add_response(json={"group_by": buckets, "meta": {}})
    result = await client.works.group_by("type")
    assert all(isinstance(bucket, GroupByBucket) for bucket in result)
    assert result[0].count == buckets[0]["count"]


async def test_autocomplete_parses_rows(client, httpx_mock):
    rows = load_fixture("autocomplete.json")["results"]
    httpx_mock.add_response(json={"results": rows})
    result = await client.autocomplete("utrecht")
    assert len(result) == len(rows)
    assert httpx_mock.get_requests()[-1].url.params["q"] == "utrecht"


async def test_typed_autocomplete_route(client, httpx_mock):
    rows = load_fixture("autocomplete.json")["results"][:1]
    httpx_mock.add_response(json={"results": rows})
    result = await client.autocomplete("utrecht", entity_type="institutions")
    assert len(result) == 1
    assert httpx_mock.get_requests()[-1].url.path == "/autocomplete/institutions"
