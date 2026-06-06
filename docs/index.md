# Syntheca

**Python interface for the OpenAlex API**, built on [bibliofabric](https://github.com/utsmok/bibliofabric).

Syntheca provides a fully-typed, async-first Python client for [OpenAlex](https://openalex.org) — the open catalog of the global research system. It wraps all eight entity endpoints (Works, Authors, Sources, Institutions, Topics, Keywords, Publishers, Funders) with Pydantic models, structured filters, and cursor-based pagination.

## Why syntheca?

- **Async-native** — every operation is `async`, designed for modern Python (3.12+).
- **Typed end-to-end** — Pydantic v2 models for all entities and filter parameters, with full IDE autocomplete.
- **Ergonomic API** — `async with SynthecaSession() as session:` gives you access to every endpoint through attribute access.
- **Built on bibliofabric** — inherits robust HTTP handling, retry logic, and response unwrapping from a shared framework.

## Quick peek

```python
import asyncio
from syntheca import SynthecaSession

async def main():
    async with SynthecaSession() as session:
        work = await session.works.get("W2741809807")
        print(work.display_name)

asyncio.run(main())
```

## Features

| Feature | Description |
|---|---|
| Entity clients | Works, Authors, Sources, Institutions, Topics, Keywords, Publishers, Funders |
| Pydantic filter models | `WorksFilters(authorships_author_id="A123")` → `authorships.author.id:A123` |
| Cursor pagination | `async for work in session.works.iterate(...):` |
| Convenience queries | `session.queries.works_by_author("...")`, `citing_works(...)`, etc. |
| Helper utilities | DOI normalization, OpenAlex ID parsing, abstract reconstruction |
| API key support | Env var `SYNTHECA_OPENALEX_API_KEY` or explicit `api_key=` parameter |

## Next steps

- [Getting Started](getting_started.md) — install, authenticate, run your first query
- [Installation](installation.md) — detailed install instructions and Python version requirements
- [Usage Basics](usage_basics.md) — sessions, searching, iterating, collecting
- [Authentication](authentication.md) — API keys and the polite pool
- [API Reference](api_reference.md) — auto-generated module docs
- [Contributing](contributing.md) — development setup, testing, linting
