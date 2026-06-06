# Getting Started

Install aletheca, set up authentication, and run your first query in under two minutes.

## 1. Install

```bash
pip install aletheca
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add aletheca
```

See [Installation](installation.md) for Python version requirements and optional dependencies.

## 2. Authenticate (optional)

The OpenAlex API works without an API key, but you'll be in the "polite pool" (slower). For faster responses, set your API key as an environment variable:

```bash
export ALETHECA_OPENALEX_API_KEY="your-key-here"
```

Or pass it directly in code. See [Authentication](authentication.md) for details.

## 3. Fetch a work

```python
import asyncio
from aletheca import AlethecaSession


async def main():
    async with AlethecaSession() as session:
        # Get a single work by OpenAlex ID
        work = await session.works.get("W2741809807")
        print(f"Title: {work.display_name}")
        print(f"Year:  {work.publication_year}")
        print(f"Citations: {work.cited_by_count}")


asyncio.run(main())
```

## 4. Search and iterate

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters


async def search_open_access():
    async with AlethecaSession() as session:
        # Search for open-access works about machine learning, published in 2024
        filters = WorksFilters(
            default_search="machine learning",
            is_oa=True,
            publication_year=2024,
        )

        async for work in session.works.iterate(filters=filters, per_page=50):
            print(work.display_name)
```

## 5. Use convenience queries

Aletheca bundles common multi-step workflows into query functions:

```python
from aletheca import AlethecaSession


async def author_works():
    async with AlethecaSession() as session:
        # Fetch all works by an author (looks up author ID from name)
        works = await session.queries.works_by_author("John Smith", limit=20)
        for work in works:
            print(work.display_name)


asyncio.run(author_works())
```

!!! tip "What's next?"
    Read [Usage Basics](usage_basics.md) for a complete walkthrough of sessions, filtering, pagination, and the convenience query interface.
