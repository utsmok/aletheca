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

Or with pip: `pip install aletheca`. Requires Python >=3.12.

## Quick Start

```python
import asyncio
from aletheca import AlethecaSession

async def main():
    async with AlethecaSession() as session:
        # Get a work by OpenAlex ID
        work = await session.works.get("W1234567890")
        print(work.title)

        # Search works
        results = await session.works.search(search="machine learning", page_size=10)
        for work in results.results:
            print(f"{work.title} ({work.publication_year})")

        # Iterate all works by an author (cursor-based auto-pagination)
        async for work in session.works.iterate(
            filters={"authorships.author.id": "A1234567890"},
            page_size=200,
        ):
            print(work.title)

asyncio.run(main())
```

No authentication required -- the OpenAlex API works without it. For higher rate limits, see [Authentication](https://utsmok.github.io/aletheca/authentication/).

## Examples

All examples in [`examples/`](examples/) are dual-purpose -- run as scripts or as interactive [marimo](https://marimo.io) notebooks:

```bash
# As a script
uv run examples/simple_example.py

# As an interactive notebook
uv run marimo edit examples/simple_example.py
```

| Script | Description |
|--------|-------------|
| `simple_example.py` | Search, iterate, get works |
| `02_filtering_and_search.py` | WorksFilters, AuthorsFilters, and other filter models |
| `03_institution_research.py` | Works by institution, topic analysis |
| `04_author_discovery.py` | Find authors, retrieve their works |
| `05_advanced_queries.py` | Cursor pagination, select fields, sort |
| `06_convenience_queries.py` | `session.queries.*` convenience functions |
| `07_iterator_helpers.py` | `collect()`, `count()`, `first()` from bibliofabric mixins |
| `08_safe_types_and_helpers.py` | SafeList, SafeStr, DOI normalization, abstract reconstruction |

See [`examples/README.md`](examples/README.md) for details on running examples as interactive marimo notebooks.

## Authentication

Aletheca auto-detects the OpenAlex API key from environment variables or `.env` files (prefixed with `ALETHECA_`). No auth is the default if nothing is configured.

```dotenv
ALETHECA_OPENALEX_API_KEY=your_api_key
```

Or pass explicitly:

```python
async with AlethecaSession(api_key="your_api_key") as session:
    ...
```

With an API key you get faster responses (dedicated pool). Without one, you use the polite pool (slower).

→ **Full guide:** [Authentication](https://utsmok.github.io/aletheca/authentication/)

## Basic Usage

### Get a single entity

```python
work = await session.works.get("W2741809801")
print(work.title, work.doi, work.publication_year)
```

### Search

```python
results = await session.works.search(search="machine learning", page_size=5)
for work in results.results:
    print(work.title)
```

### Iterate all results

```python
async for work in session.works.iterate(
    filters={"publication_year": 2024, "is_oa": True},
    page_size=200,
):
    print(work.title)
    break  # stop when you want
```

### Convenience queries

```python
citations = await session.queries.citing_works("W2741809801")
print(f"{len(citations)} citations")
```

→ **Full guide:** [Usage Basics](https://utsmok.github.io/aletheca/usage_basics/) · [Works](https://utsmok.github.io/aletheca/usage/works/) · [All Entities](https://utsmok.github.io/aletheca/api_reference/)

## Known OpenAlex API Issues

Full bug report with reproduction steps: [`OPENALEX_BUG_REPORT.md`](OPENALEX_BUG_REPORT.md).

- **OpenAPI spec is substantially incomplete** -- 50+ fields returned by the live API are missing from the spec schemas across all entity types. Several spec fields don't exist in the live API.
- **Wrong field names in spec** -- `content_url` (spec) vs `content_urls` (live), `grants_count` (spec) vs `awards_count` (live)
- **Undocumented fields** -- `institution_awarded` on Awards is not documented anywhere; 15+ nested Award filters are missing from the docs filter table
- **Awards endpoint missing from `llms.txt`** -- the awards endpoint is not listed in the API quick reference
- **`per_page` max is 200, not 100** -- documented as 100 but the API accepts 200
- **Keyword IDs are slug paths, not short IDs** -- live keyword records carry ids like `https://openalex.org/keywords/photosynthesis`, and the single-record route rejects that full-URL form (nested slashes → HTML 404) even though `/works/https://openalex.org/W…` is accepted. `get()` normalizes both forms.
- **Awards 400 body is the authoritative filter list** -- the awards endpoint rejects several filters its docs summaries suggest (`funder.country_code`, plain `display_name`, `lead_investigator.id`, `from_/to_*_date`) and its 400 error body enumerates all 40 valid filters, which is more complete than any docs table.

## Development

```bash
uv sync --all-groups --all-extras         # install everything
uv run ruff check src/ --fix              # lint
uv run ruff format src/                   # format
uvx ty check src/                         # type check
uv run pytest tests/                      # run tests
uv run pytest --cov=aletheca tests/       # coverage (CI threshold: 95%)
uv build                                  # build package
uv run mkdocs serve                       # local docs
```

Contributions welcome -- see [Contributing](https://utsmok.github.io/aletheca/contributing/).

## License

MIT
