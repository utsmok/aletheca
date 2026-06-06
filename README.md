# Syntheca

Python interface for the [OpenAlex API](https://docs.openalex.org/), built on the [bibliofabric](https://github.com/utsmok/bibliofabric) framework.

## Installation

```bash
pip install syntheca
```

## Quick Start

```python
import asyncio
from syntheca import SynthecaSession

async def main():
    async with SynthecaSession() as session:
        # Get a work by OpenAlex ID
        work = await session.works.get("W1234567890")
        print(work.title)

        # Search works
        results = await session.works.search(search="machine learning", page_size=10)
        for work in results.results:
            print(f"{work.title} ({work.publication_year})")

        # Iterate all works by an author
        async for work in session.works.iterate(
            filters={"authorships.author.id": "A1234567890"},
            page_size=200,
        ):
            print(work.title)

asyncio.run(main())
```

## Authentication

Set your OpenAlex API key via environment variable:

```bash
export SYNTHECA_OPENALEX_API_KEY=your_api_key
```

Or pass it directly:

```python
async with SynthecaSession(api_key="your_api_key") as session:
    ...
```

## Features

- **Async-first**: Built on `httpx` with `asyncio`
- **Typed models**: Pydantic v2 models for all OpenAlex entities
- **Cursor pagination**: Efficient iteration over large result sets
- **Filter serialization**: Automatic conversion to OpenAlex `filter=key:value` syntax
- **Safe types**: `SafeList` and `SafeStr` for None-safe traversal
- **Convenience queries**: High-level functions for common workflows

## Development

```bash
# Install with all dev dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Lint
uv run ruff check src/
uv run ruff format src/
```

## License

MIT
