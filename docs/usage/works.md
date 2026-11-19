# Works

`client.works` talks to the `/works` endpoint and returns `Work` models. It supports the shared operations (`get`, `search`, `iterate`, `collect`, `first`, `count`) plus the works-only features described below.

```python
work = await client.works.get("W2741809807")
```

IDs may be bare (`W2741809807`) or full URLs (`https://openalex.org/W2741809807`); both normalize to the same path and dictionary key.

## Search

```python
from aletheca import WorksFilters

page = await client.works.search(
    WorksFilters(publication_year=2024, is_oa=True),
    query="photosynthesis",
    sort="cited_by_count:desc",
    select=["id", "title", "doi"],
    page_size=100,
)
for work in page.results:
    print(work.title)
```

`search()` returns one `Page[Work]`: `page.results`, `page.total` (`meta.count`), `page.next_cursor`, and `page.meta` (remaining envelope fields such as `cost_usd` or `group_by` buckets). The default page size is 25; OpenAlex accepts at most 100.

Corpus controls travel as separate query parameters, not filters:

```python
page = await client.works.search(filters, corpus="expansion")
page = await client.works.search(filters, include_parts=True, include_pulled=True)
```

Valid `corpus` values are `core` (default upstream), `expansion`, and `all`; anything else raises `ConfigurationError` before a request is sent.

Pass `rerank=True` to reorder the top 100 of a relevance-sorted search (it costs 10 extra credits and needs the relevance sort a `query` gives you). The response reports whether reranking applied:

```python
page = await client.works.search(query="photosynthesis", rerank=True)
page.meta["reranked"]  # True when OpenAlex reranked the results
```

## Iterating over all matches

```python
async for work in client.works.iterate({"authorships.author.id": "A5089275346"}):
    ...
```

`iterate()` pages with cursors at `per-page=100` and yields `Work` objects. It accepts `limit`, an `on_page(page_number, next_cursor)` callback for checkpointing, and `on_error="skip"` to drop records that fail validation. Keyless access can fetch only the first cursor page; the follow-up 401 raises `AuthError` with a message that names `ALETHECA_API_KEY`.

## Counting at minimal cost

```python
n = await client.works.count({"is_oa": True})
```

`count()` sends `per-page=1` with `select=id`, so the request carries no entity payloads.

## Batch retrieval

```python
works = await client.works.batch_get_by_doi(
    ["10.7717/peerj.4375", "https://doi.org/10.1038/nature12373"]
)
works = await client.works.batch_get_by_openalex_id(["W2741809807", "W2100837269"])
```

Both return `dict[normalized id, Work]`. Ids are deduplicated, split into chunks of 100 (OpenAlex's pipe-joined OR cap), and fetched concurrently. DOIs are normalized: URL prefixes are stripped and the value lowercased. Missing records are absent from the result; works without the requested field fall back to their OpenAlex id as key. `batch_get(ids, field=..., batch_size=...)` is the generic form; passing more than 100 OR values in one filter raises `ConfigurationError`.

## PDF links

```python
urls = await client.works.oa_pdf_urls("10.7717/peerj.4375")
```

`oa_pdf_urls()` fetches the work once and returns its downloadable PDF URLs (`list[str]`): the copy in `best_oa_location` first, then `primary_location`, then the remaining `locations`, with duplicates dropped. It returns `[]` when no location carries a PDF. OpenAlex's own paid PDF copies (`work.content_urls.pdf`, 100 credits each) are not included.

## Citation graph

```python
citing = await client.works.citing("W2741809807", limit=100)
refs = await client.works.referenced("W2741809807", limit=100)
```

`citing()` runs a cursor query with `filter=cites:<id>` and collects up to `limit` works. `referenced()` fetches the work once, reads its `referenced_works` list, and batch-fetches up to `limit` targets.

## Random samples

```python
page = await client.works.sample(1_000, seed=42)
```

`sample(n)` sends `sample=n` (maximum 10,000) and optionally `seed` for reproducible draws. `page.total` reports the sample size, not the corpus size.

## Group by

```python
buckets = await client.works.group_by("type")
multi = await client.works.group_by("type,publication_year")
```

Returns typed `GroupByBucket` objects. Multi-field group-by nests deeper dimensions in `bucket.groups`. Responses page at 200 buckets with a cursor; pass `cursor=<next cursor>` (from the last request's `meta.next_cursor`) to continue.

## Scoped search

Only one search parameter is allowed per request, so the `search.*` fields have their own entry point:

```python
page = await client.works.search_scoped("machine learning", scope="title_and_abstract")
```

Scopes: `title`, `title_and_abstract`, `title_abstract_keywords`, `exact` (wildcards and proximity operators), and `semantic` (embedding search; at most 50 results, 1 request per second). A search costs more credits than a plain list request; see [errors, retries, and rate limits](../errors.md).

## Filters

`WorksFilters` covers the common filters, including `publication_year`, `is_oa`, `doi`, `cites:W...`, `cited_by:W...`, `related_to:W...`, dot-notation fields such as `authorships.author.id`, `primary_location.source.id`, `topics.id`, and the part-of filters `has_parent_work`, `parent_works.id`, `parent_works.relationship`, `lineage`, and `child_works_count`. Every model allows extra fields, so filters that are missing here still work as dicts: `client.works.search({"some.new.filter": "x"})`.

Booleans serialize lowercase (`is_oa:true`), list values join into `|` OR groups, and DOI-valued filters are normalized before serialization.
