"""Outgoing request shape: paths, params, filter syntax, paging, batching."""

import pytest

from aletheca import ConfigurationError, WorksFilters

from .conftest import entity, envelope, load_fixture

WORK = load_fixture("work.json")


def last_params(httpx_mock) -> dict[str, str]:
    request = httpx_mock.get_requests()[-1]
    return dict(request.url.params)


async def test_get_uses_entity_path(client, httpx_mock):
    httpx_mock.add_response(json=WORK)
    work = await client.works.get("W2741809807")
    assert work.id == WORK["id"]
    assert httpx_mock.get_requests()[-1].url.path == "/works/W2741809807"


async def test_get_normalizes_url_ids(client, httpx_mock):
    httpx_mock.add_response(json=WORK)
    await client.works.get("https://openalex.org/W2741809807")
    assert httpx_mock.get_requests()[-1].url.path == "/works/W2741809807"


async def test_search_params_shape(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search(
        {"publication_year": 2024, "is_oa": True},
        query="open science",
        sort="display_name:asc",
        select=["id", "title"],
        page=2,
        page_size=10,
    )
    params = last_params(httpx_mock)
    assert params["filter"] == "publication_year:2024,is_oa:true"
    assert params["search"] == "open science"
    assert params["sort"] == "display_name:asc"
    assert params["select"] == "id,title"
    assert params["per-page"] == "10"
    assert params["page"] == "2"


async def test_search_defaults_to_25_per_page(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search()
    assert last_params(httpx_mock)["per-page"] == "25"


async def test_search_page_size_capped_at_100(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search(page_size=500)
    assert last_params(httpx_mock)["per-page"] == "100"


async def test_filter_model_uses_dot_aliases(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    filters = WorksFilters(authorships_author_id="A123", is_oa=True)
    await client.works.search(filters)
    assert set(last_params(httpx_mock)["filter"].split(",")) == {
        "authorships.author.id:A123",
        "is_oa:true",
    }


async def test_list_values_become_pipe_joined_or(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search({"openalex": ["W1", "W2", "W3"]})
    assert last_params(httpx_mock)["filter"] == "openalex:W1|W2|W3"


async def test_doi_filter_values_are_normalized(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search({"doi": "https://doi.org/10.1234/ABC"})
    assert last_params(httpx_mock)["filter"] == "doi:10.1234/abc"


async def test_more_than_100_or_values_rejected(client, httpx_mock):
    with pytest.raises(ConfigurationError):
        await client.works.search({"openalex": [f"W{i}" for i in range(101)]})


async def test_sort_sequence_is_comma_joined(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search(sort=["display_name:asc", "cited_by_count:desc"])
    assert last_params(httpx_mock)["sort"] == "display_name:asc,cited_by_count:desc"


async def test_iterate_pages_with_cursor_at_100_per_page(client, httpx_mock):
    httpx_mock.add_response(json=envelope([entity("W1")], next_cursor="I1"))
    httpx_mock.add_response(json=envelope([entity("W2")]))
    collected = [work async for work in client.works.iterate()]
    assert [work.id for work in collected] == [
        "https://openalex.org/W1",
        "https://openalex.org/W2",
    ]
    requests = httpx_mock.get_requests()
    assert dict(requests[0].url.params)["cursor"] == "*"
    assert dict(requests[0].url.params)["per-page"] == "100"
    assert dict(requests[1].url.params)["cursor"] == "I1"


async def test_iterate_respects_limit_and_on_page(client, httpx_mock):
    httpx_mock.add_response(
        json=envelope([entity("W1"), entity("W2")], next_cursor="I1"),
    )
    checkpoints = []
    collected = [
        work
        async for work in client.works.iterate(
            limit=1, on_page=lambda n, c: checkpoints.append((n, c))
        )
    ]
    assert len(collected) == 1
    assert checkpoints == [(1, "I1")]
    assert len(httpx_mock.get_requests()) == 1


async def test_count_requests_minimal_payload(client, httpx_mock):
    httpx_mock.add_response(json=envelope([], count=42))
    assert await client.works.count() == 42
    params = last_params(httpx_mock)
    assert params["per-page"] == "1"
    assert params["select"] == "id"
    assert params["cursor"] == "*"


async def test_corpus_and_include_flags_stay_out_of_filter(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search(
        None, corpus="expansion", include_parts=True, include_pulled=False
    )
    params = last_params(httpx_mock)
    assert params["corpus"] == "expansion"
    assert params["include_parts"] == "true"
    assert params["include_pulled"] == "false"
    assert "filter" not in params


async def test_invalid_corpus_rejected(client, httpx_mock):
    with pytest.raises(ConfigurationError):
        await client.works.search(None, corpus="bogus")


async def test_sample_sends_sample_and_seed(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.sample(50, seed=42)
    params = last_params(httpx_mock)
    assert params["sample"] == "50"
    assert params["seed"] == "42"


async def test_sample_rejects_out_of_range(client, httpx_mock):
    with pytest.raises(ConfigurationError):
        await client.works.sample(0)


async def test_scoped_search_uses_search_dot_param(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search_scoped("photosynthesis", scope="title_abstract_keywords")
    assert last_params(httpx_mock)["search.title_abstract_keywords"] == "photosynthesis"


async def test_group_by_sends_group_by_param(client, httpx_mock):
    buckets = load_fixture("group_by.json")["group_by"]
    httpx_mock.add_response(json={"group_by": buckets, "meta": {"count": 2}})
    result = await client.works.group_by("type")
    assert result[0].key == buckets[0]["key"]
    assert last_params(httpx_mock)["group_by"] == "type"


async def test_batch_get_splits_at_100_and_keys_results(client, httpx_mock):
    ids = [f"W{i}" for i in range(103)]
    chunk1 = [entity(f"W{i}") for i in range(100)]
    chunk2 = [entity(f"W{i}") for i in range(100, 103)]
    httpx_mock.add_response(json=envelope(chunk1, count=100))
    httpx_mock.add_response(json=envelope(chunk2, count=3))
    result = await client.works.batch_get(ids, field="openalex")
    assert len(result) == 103
    assert "W1" in result and "W102" in result
    requests = httpx_mock.get_requests()
    assert dict(requests[0].url.params)["filter"] == "openalex:" + "|".join(
        f"W{i}" for i in range(100)
    )
    assert dict(requests[0].url.params)["per-page"] == "100"
    assert dict(requests[1].url.params)["filter"] == "openalex:W100|W101|W102"
    assert dict(requests[1].url.params)["per-page"] == "3"


async def test_batch_get_by_doi_normalizes_keys(client, httpx_mock):
    records = [
        {"id": "https://openalex.org/W1", "doi": "https://doi.org/10.1234/abc"},
        {"id": "https://openalex.org/W2", "doi": "10.5678/def"},
    ]
    httpx_mock.add_response(json=envelope(records, count=2))
    result = await client.works.batch_get_by_doi(
        ["https://doi.org/10.1234/ABC", "10.5678/DEF"]
    )
    assert sorted(result) == ["10.1234/abc", "10.5678/def"]
    params = last_params(httpx_mock)
    assert params["filter"] == "doi:10.1234/abc|10.5678/def"


async def test_citing_filters_by_cites(client, httpx_mock):
    httpx_mock.add_response(json=envelope([entity("W9")]))
    citing = await client.works.citing("W2741809807", limit=5)
    assert len(citing) == 1
    params = last_params(httpx_mock)
    assert params["filter"] == "cites:W2741809807"
    assert params["cursor"] == "*"


async def test_referenced_works_fetches_targets(client, httpx_mock):
    httpx_mock.add_response(
        json={**WORK, "referenced_works": [WORK["id"], "https://openalex.org/W999"]},
    )
    httpx_mock.add_response(
        json=envelope([{"id": WORK["id"], "display_name": WORK["title"]}], count=1),
    )
    referenced = await client.works.referenced("W2741809807", limit=10)
    assert referenced[0].id == WORK["id"]
    params = last_params(httpx_mock)
    assert params["filter"] == "openalex:W2741809807|W999"


async def test_other_resources_use_their_paths(client, httpx_mock):
    for name, path in [
        ("authors", "authors"),
        ("sources", "sources"),
        ("institutions", "institutions"),
        ("topics", "topics"),
        ("keywords", "keywords"),
        ("publishers", "publishers"),
        ("funders", "funders"),
        ("awards", "awards"),
    ]:
        httpx_mock.add_response(json=envelope([]))
        page = await getattr(client, name).search()
        assert httpx_mock.get_requests()[-1].url.path == f"/{path}"
        assert page.results == []
