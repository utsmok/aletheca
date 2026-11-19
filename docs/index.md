# Aletheca

Aletheca is an async Python client for the [OpenAlex API](https://docs.openalex.org/), built on [bibliofabric](https://github.com/utsmok/bibliofabric). It types all nine entity endpoints (works, authors, sources, institutions, topics, keywords, publishers, funders, awards) with Pydantic models and serializes OpenAlex filter syntax for you.

## Install

```bash
uv add aletheca
```

Requires Python 3.12 or newer.

## Authentication

OpenAlex works without a key, but unkeyed traffic shares a $0.10/day per-IP budget and cannot use cursor paging past the first page. A free key raises the budget to $1/day. Request one at [openalex.org/settings/api](https://openalex.org/settings/api), then export it:

```bash
export ALETHECA_API_KEY="your-key"
```

By default the key travels as the `api_key` query parameter. Set `ALETHECA_AUTH_SCHEME=bearer` to send it as an `Authorization: Bearer` header instead. See [errors, retries, and rate limits](errors.md) for budgets and pacing.

## Quick start

```python
import asyncio
from aletheca import AlethecaClient


async def main():
    async with AlethecaClient() as client:
        work = await client.works.get("W2741809807")
        print(work.title, work.publication_year)

        page = await client.works.search(
            {"is_oa": True, "publication_year": 2024},
            query="photosynthesis",
            select=["id", "title"],
        )
        print(page.total, len(page.results))

        async for author in client.authors.iterate(
            {"last_known_institutions.id": "I1290904741"}
        ):
            print(author.display_name)


asyncio.run(main())
```

Every resource client exposes `get()`, `search()`, `iterate()`, `collect()`, `first()`, and `count()`. The works client adds OpenAlex-specific helpers: `batch_get_by_doi()`, `citing()`, `referenced()`, `group_by()`, `sample()`, and `search_scoped()`. The client itself offers free `autocomplete()` and `rate_limit()` endpoints.

## Settings

`AlethecaSettings` loads from environment variables prefixed with `ALETHECA_`: `ALETHECA_API_KEY`, `ALETHECA_AUTH_SCHEME`, `ALETHECA_MAX_REQUESTS_PER_SECOND`, `ALETHECA_MAX_CONCURRENCY`, `ALETHECA_TIMEOUT`, `ALETHECA_MAX_RETRIES`, `ALETHECA_MAX_RETRY_WAIT`, `ALETHECA_USER_AGENT`. The legacy `ALETHECA_OPENALEX_API_KEY` name still works.

## Where to go next

- One usage page per resource family: start with [works](usage/works.md).
- [Errors, retries, and rate limits](errors.md).
- [Upstream quirks](upstream-quirks.md) observed in the live OpenAlex API.
- The [API reference](reference.md) is generated from the source.
