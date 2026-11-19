"""Ergonomics features: the locations and links resources, works rerank,
and works.oa_pdf_urls."""

import json

from aletheca import Link, LocationRecord

from .conftest import envelope, load_fixture

LOCATION = load_fixture("location.json")
LINKS_PAGE = load_fixture("links_page.json")
RERANK_PAGE = load_fixture("work_search_rerank.json")
WORK_MULTI_OA = load_fixture("work_multi_oa.json")


def last_params(httpx_mock) -> dict[str, str]:
    return dict(httpx_mock.get_requests()[-1].url.params)


# --- /locations -------------------------------------------------------


async def test_locations_get_by_namespaced_id(client, httpx_mock):
    httpx_mock.add_response(json=LOCATION)
    record = await client.locations.get("doi:10.7717/peerj.4375")
    assert httpx_mock.get_requests()[-1].url.path == (
        "/locations/doi:10.7717/peerj.4375"
    )
    assert isinstance(record, LocationRecord)
    assert record.id == LOCATION["id"]
    assert record.work_id == LOCATION["work_id"]
    assert record.native_id_namespace == "doi"
    assert record.source_name == "PeerJ"
    assert record.is_retracted is False
    assert record.urls[0].url == LOCATION["urls"][0]["url"]
    assert record.urls[0].content_type == "html"
    assert record.ids[0].namespace == "eissn"


async def test_locations_search_shape_and_parse(client, httpx_mock):
    httpx_mock.add_response(json=envelope([LOCATION], count=1))
    page = await client.locations.search({"doi": "10.7717/peerj.4375"})
    params = last_params(httpx_mock)
    assert params["filter"] == "doi:10.7717/peerj.4375"
    assert params["per-page"] == "25"
    assert page.total == 1
    assert page.results[0].id == LOCATION["id"]


# --- /links -----------------------------------------------------------


async def test_links_origin_sends_filter_and_parses(client, httpx_mock):
    httpx_mock.add_response(json=LINKS_PAGE)
    edges = await client.links.origin("https://openalex.org/W2741809807")
    assert last_params(httpx_mock)["filter"] == "origin:W2741809807"
    assert len(edges) == len(LINKS_PAGE["results"])
    assert all(isinstance(edge, Link) for edge in edges)
    assert edges[0].target == LINKS_PAGE["results"][0]["target"]
    assert edges[0].relationship == "https://openalex.org/relationships/citation"


async def test_links_target_sends_target_filter(client, httpx_mock):
    httpx_mock.add_response(json=envelope([LINKS_PAGE["results"][0]], count=1))
    edges = await client.links.target("W2741809807", limit=5)
    assert last_params(httpx_mock)["filter"] == "target:W2741809807"
    assert edges[0].origin == LINKS_PAGE["results"][0]["origin"]


# --- rerank -----------------------------------------------------------


async def test_search_rerank_param_and_meta_flag(client, httpx_mock):
    httpx_mock.add_response(json=RERANK_PAGE)
    page = await client.works.search(query="open peer review", rerank=True)
    assert last_params(httpx_mock)["rerank"] == "true"
    assert page.meta["reranked"] is True
    assert page.results[0].id == RERANK_PAGE["results"][0]["id"]
    assert page.total == RERANK_PAGE["meta"]["count"]


async def test_search_omits_rerank_by_default(client, httpx_mock):
    httpx_mock.add_response(json=envelope([]))
    await client.works.search(query="open peer review")
    assert "rerank" not in last_params(httpx_mock)


# --- oa_pdf_urls ------------------------------------------------------


async def test_oa_pdf_urls_best_oa_first_and_deduped(client, httpx_mock):
    httpx_mock.add_response(json=WORK_MULTI_OA)
    urls = await client.works.oa_pdf_urls("10.48550/arXiv.1706.03762")
    # works.get() lowers DOIs to the bare form; the single route accepts it.
    assert httpx_mock.get_requests()[-1].url.path == "/works/10.48550/arxiv.1706.03762"
    best = WORK_MULTI_OA["best_oa_location"]["pdf_url"]
    second = "https://langtaosha.org.cn/index.php/lts/preprint/download/10/108"
    # best_oa_location and primary_location carry the same pdf_url; the
    # duplicate keeps its first position and the remaining location follows.
    assert urls == [best, second]


async def test_oa_pdf_urls_skips_null_pdfs(client, httpx_mock):
    work = load_fixture("work.json")
    httpx_mock.add_response(json=work)
    urls = await client.works.oa_pdf_urls(work["id"])
    assert urls == [loc["pdf_url"] for loc in work["locations"] if loc.get("pdf_url")]


async def test_oa_pdf_urls_empty_when_no_pdf(client, httpx_mock):
    payload = json.loads(json.dumps(WORK_MULTI_OA))
    for loc in [
        payload["best_oa_location"],
        payload["primary_location"],
        *payload["locations"],
    ]:
        loc["pdf_url"] = None
    httpx_mock.add_response(json=payload)
    assert await client.works.oa_pdf_urls(payload["id"]) == []
