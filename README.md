# Aletheca: Asynchronous Python client for the OpenAlex API

Samuel Mok -- s.mok@utwente.nl -- 2025-2026

Aletheca is an async Python client for the [OpenAlex API](https://docs.openalex.org/), built on [bibliofabric](https://github.com/utsmok/bibliofabric).

**Docs:** [utsmok.github.io/aletheca](https://utsmok.github.io/aletheca/) -- **PyPI:** [aletheca](https://pypi.org/project/aletheca/) -- **License:** MIT

## Features

- **Async by design** -- built on `httpx` + `asyncio` with proper connection pooling
- **Typed throughout** -- Pydantic v2 models for all entities, PEP 561 `py.typed` marker
- **Cursor pagination** -- efficient iteration over large result sets via cursor-based auto-pagination
- **Filter serialization** -- automatic conversion to OpenAlex `filter=key:value` syntax with Pydantic filter models
- **Safe types** -- `SafeList` and `SafeStr` for None-safe traversal of API responses
- **Convenience queries** -- high-level functions for common workflows (`works_by_author`, `citing_works`, etc.)

## Installation

```bash
uv add aletheca
```

Requires Python >=3.12.

## Quick Start

```python
import asyncio
from aletheca import AlethecaClient

async def main():
    async with AlethecaClient() as client:
        # Get a work by OpenAlex ID (URL forms like https://doi.org/... also work)
        work = await client.works.get("W1234567890")
        print(work.title)

        # Search works (one page)
        page = await client.works.search(query="machine learning", page_size=10)
        for work in page.results:
            print(f"{work.title} ({work.publication_year})")

        # Iterate over matches with cursor auto-pagination (per-page=100 default)
        async for work in client.works.iterate(
            filters={"authorships.author.id": "A1234567890"},
        ):
            print(work.title)

asyncio.run(main())
```

Other resource methods: `count()` (minimal-cost `select=id` request), `batch_get(ids, field=..., batch_size=...)`, `batch_get_by_doi(dois)`, `group_by(...)`, `sample(n, seed=...)`, `search_scoped(...)` (`search.title_and_abstract`, `search.exact`, `search.semantic`), and the `corpus=`/`include_pulled=` parameters on `client.works.search(...)`. The client also exposes `client.autocomplete(query)` (free) and `client.rate_limit()` (free budget check).

## Examples

All examples in [`examples/`](examples/) are dual-purpose -- run as scripts or as interactive [marimo](https://marimo.io) notebooks:

```bash
# As a script
uv run examples/quickstart.py
```

| Script | Description |
|--------|-------------|
| `quickstart.py` | Get, count, and search works |
| `search_and_iterate.py` | Filter models, scoped search, cursor iteration |
| `batch_and_citations.py` | `batch_get_by_doi()`, `citing()`, `referenced()`, `rate_limit()` |

See [`examples/README.md`](examples/README.md) for run instructions.

## Authentication

OpenAlex has no polite pool: since February 2026 the API ignores `mailto` and meters unkeyed traffic at $0.10/day per IP address. A free API key raises the budget to $1/day and is required for cursor paging beyond the first page. Get one at [openalex.org/settings/api](https://openalex.org/settings/api).

Aletheca reads the key from the environment or `.env` (prefix `ALETHECA_`):

```dotenv
ALETHECA_API_KEY=your_api_key          # ALETHECA_OPENALEX_API_KEY also accepted
```

Or pass it explicitly:

```python
async with AlethecaClient(api_key="your_api_key") as client:
    ...
```

The key is sent as the `api_key` query parameter by default; pass `auth_scheme="bearer"` (or set `ALETHECA_AUTH_SCHEME=bearer`) to send it as an `Authorization: Bearer` header instead.

→ **Full guide:** [docs index](https://utsmok.github.io/aletheca/) and [errors, retries, and rate limits](https://utsmok.github.io/aletheca/errors/)

## Basic Usage

### Get a single entity

```python
work = await client.works.get("W2741809801")
print(work.title, work.doi, work.publication_year)
```

### Search

```python
page = await client.works.search(query="machine learning", page_size=5)
for work in page.results:
    print(work.title)
```

### Iterate all results

```python
async for work in client.works.iterate(
    filters={"publication_year": 2024, "is_oa": True},
):
    print(work.title)
    break  # stop when you want
```

### Citations and references

```python
citations = await client.works.citing("W2741809801", limit=100)
refs = await client.works.referenced("W2741809801", limit=100)
print(f"{len(citations)} citing works, {len(refs)} references fetched")
```

→ **Full guide:** [Works](https://utsmok.github.io/aletheca/usage/works/) · [all entity pages](https://utsmok.github.io/aletheca/) · [API reference](https://utsmok.github.io/aletheca/reference/)

## Known OpenAlex API Issues

Verified findings: [`docs/upstream-quirks.md`](docs/upstream-quirks.md).

- **OpenAPI spec is substantially incomplete** -- 50+ fields returned by the live API are missing from the spec schemas across all entity types. Several spec fields don't exist in the live API.
- **Wrong field names in spec** -- `content_url` (spec) vs `content_urls` (live), `grants_count` (spec) vs `awards_count` (live)
- **Undocumented fields** -- `institution_awarded` on Awards is not documented anywhere; 15+ nested Award filters are missing from the docs filter table
- **Awards endpoint missing from `llms.txt`** -- the awards endpoint is not listed in the API quick reference
- **`per_page` max is 100** -- 200 still works but is deprecated legacy behavior, slated for removal (OpenAlex docs, 2026-08); all examples here use 100
- **Keyword IDs are slug paths, not short IDs** -- live keyword records carry ids like `https://openalex.org/keywords/photosynthesis`, and the single-record route rejects that full-URL form (nested slashes → HTML 404) even though `/works/https://openalex.org/W…` is accepted. `get()` normalizes both forms.
- **Awards 400 body is the authoritative filter list** -- the awards endpoint rejects several filters its docs summaries suggest (`funder.country_code`, plain `display_name`, `lead_investigator.id`, `from_/to_*_date`) and its 400 error body enumerates all 40 valid filters, which is more complete than any docs table.

## Development

```bash
uv sync --all-groups     # install everything
uv run ruff check --fix  # lint
uv run ruff format       # format
uv run ty check src      # type check
uv run pytest            # offline tests; add -m live_api for live smoke tests
uv build                 # build package
uv run mkdocs serve      # local docs
```

Contributions welcome -- see [Contributing](https://utsmok.github.io/aletheca/contributing/).

## License

MIT
