# Contributing

Contributions are welcome. This guide covers setting up the development environment, running tests, linting, and building documentation.

## Development setup

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager

### Clone and install

```bash
git clone https://github.com/utsmok/syntheca.git
cd syntheca
uv sync --all-groups
```

This installs the package in editable mode along with all dependency groups (`dev`, `docs`, `lint`, `test`).

??? note "Dependency groups"
    The `pyproject.toml` defines these groups:
    
    - **dev** — pytest, pytest-asyncio, pytest-cov, pytest-httpx, python-dotenv
    - **docs** — mkdocs, mkdocs-material, mkdocstrings
    - **lint** — ruff
    - **test** — pytest, pytest-randomly

## Running tests

```bash
# Run all unit tests
uv run pytest

# Run with coverage
uv run pytest --cov=syntheca

# Run a specific test file
uv run pytest tests/test_session.py

# Run with verbose output
uv run pytest -v
```

### Test markers

Tests that hit the live OpenAlex API are marked with `@pytest.mark.live_api` and are excluded by default:

```bash
# Run only live API tests (requires SYNTHECA_OPENALEX_API_KEY)
uv run pytest -m live_api
```

??? note "asyncio mode"
    The test suite uses `asyncio_mode = "auto"` in pytest — no need for `@pytest.mark.asyncio` decorators on async test functions.

## Linting and formatting

Syntheca uses **ruff** for both linting and formatting:

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix lint errors
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without writing
uv run ruff format --check .
```

### Type checking

```bash
uv run ty check .
```

## Building documentation

Documentation uses **mkdocs-material** with **mkdocstrings** for API reference generation:

```bash
# Build static docs
uv run mkdocs build

# Live preview with auto-reload
uv run mkdocs serve
```

The docs source lives in `docs/`. The mkdocs configuration is in `mkdocs.yml` at the project root.

## Project structure

```
src/syntheca/
    __init__.py          # Public API: SynthecaSession, SynthecaClient
    client.py            # SynthecaClient — async HTTP client
    session.py           # SynthecaSession — high-level context manager
    config.py            # SynthecaSettings (pydantic-settings)
    constants.py         # Base URL, defaults, user agent
    endpoints.py         # Pydantic filter models for all endpoints
    queries.py           # Convenience query functions
    _helpers.py          # DOI normalization, ID parsing, abstract reconstruction
    unwrapper.py         # OpenAlex response unwrapper (meta/results)
    py.typed             # PEP 561 marker
    models/              # Pydantic v2 entity models
        base.py          # BaseEntity, ApiResponse, Meta
        work.py          # Work, Authorship, DehydratedSource
        author.py        # Author
        source.py        # Source
        institution.py   # Institution
        topic.py         # Topic
        keyword.py       # Keyword
        publisher.py     # Publisher
        funder.py        # Funder
        award.py         # Award
        common.py        # Shared nested types (Location, OpenAccess, etc.)
        ids.py           # Entity ID models (WorkIds, AuthorIds, etc.)
        safe_types.py    # SafeStr, SafeList wrappers
    resources/           # Endpoint-specific resource clients
        _standard.py     # SynthecaResourceClient base class
        works_client.py  # WorksClient
        authors_client.py # AuthorsClient
        ...              # One client per entity
tests/
    test_*.py            # Unit and integration tests
```

## Code conventions

- **Use `uv run`** for everything — never `python`, `pip`, or manual venv activation.
- **Ruff formatting** — 88 character line length, configured in `pyproject.toml`.
- **Pydantic v2 models** — all entity models use `ConfigDict(extra="allow")` for forward-compatibility with API changes.
- **Keyword arguments** — instantiate models with keyword args, never positional.
- **Async-only** — all API operations are async. No synchronous client exists yet.
- **Typed** — the package ships `py.typed`. Preserve type annotations for downstream users.

## Pull request checklist

Before opening a PR:

1. `uv run ruff check .` passes
2. `uv run ruff format --check .` passes
3. `uv run pytest` passes
4. New functionality includes tests
5. Public API changes update `__all__` exports
