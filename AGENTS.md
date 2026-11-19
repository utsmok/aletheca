# Aletheca — Project Guide

## What It Is

Aletheca is an async Python client library for the [OpenAlex API](https://docs.openalex.org). It provides typed, ergonomic access to scholarly works, authors, sources, institutions, topics, publishers, funders, awards, and keywords.


Built on top of **bibliofabric** — a generic async API client framework providing auth, pagination, response unwrapping, and mixin-based resource operations.

**Status:** Alpha. Published on PyPI as `aletheca`.

## Architecture

```
AlethecaSession          # User-facing async context manager (session.py)
 └─ AlethecaClient       # Core HTTP client, auth resolution, resource orchestration (client.py)
     ├─ WorksClient            # mixin-based (bibliofabric)
     ├─ AuthorsClient          # mixin-based (bibliofabric)
     ├─ SourcesClient          # mixin-based (bibliofabric)
     ├─ InstitutionsClient     # mixin-based (bibliofabric)
     ├─ TopicsClient           # mixin-based (bibliofabric)
     ├─ KeywordsClient         # mixin-based (bibliofabric)
     ├─ PublishersClient       # mixin-based (bibliofabric)
     ├─ FundersClient          # mixin-based (bibliofabric)
     └─ AwardsClient           # mixin-based (bibliofabric)
```

### Key Layers

| Layer | File(s) | Role |
|-------|---------|------|
| **Session** | `session.py` | Thin async context manager wrapper around `AlethecaClient`. Entry point for users. Delegates resource access to client via `__getattr__`. |
| **Client** | `client.py` | Extends `bibliofabric.BaseApiClient`. Resolves auth strategy (QueryParameterAuth or NoAuth), initializes resource clients lazily. |
| **Resources** | `resources/*.py` | Per-endpoint clients. All inherit from `AlethecaResourceClient` (extends `BaseResourceClient`), which provides `get()` (normalizing full-URL entity IDs) and delegates to `GettableMixin`; use `SearchableMixin`, `CursorIterableMixin` via bases. Override `_param_page_size="per_page"`, `_param_sort="sort"`, and `_serialize_filters()` for OpenAlex filter syntax. |
| **Endpoints** | `endpoints.py` | Pydantic filter models per endpoint (`WorksFilters`, etc.) with `extra="allow"` and `populate_by_name=True`. Field aliases map Python names to OpenAlex dot-notation filter names (e.g., `authorships_author_id` → `authorships.author.id`). |
| **Unwrapper** | `unwrapper.py` | Implements `bibliofabric.ResponseUnwrapper` protocol. Extracts `results`, `meta.next_cursor`, `meta.count` from OpenAlex's JSON envelope. |
| **Config** | `config.py` | `AlethecaSettings(BaseApiSettings)` via pydantic-settings. Env prefix `ALETHECA_`. Reads `.env`. Cached via `@lru_cache`. |
| **Constants** | `constants.py` | Base URLs, defaults, version detection (`importlib.metadata`), user-agent string. |
| **Queries** | `queries.py` | Convenience functions (`works_by_author`, `works_by_doi`, `citing_works`, `referenced_works`, `works_by_institution`). Access via `session.queries.*`. |
| **Helpers** | `_helpers.py` | `normalize_doi`, `parse_openalex_id`, `detect_id_type`, `reconstruct_abstract`. |

### API Conventions

- **Base URL**: `https://api.openalex.org`
- **Auth**: API key via `?api_key=...` query parameter (using `QueryParameterAuth`). No key = polite pool (slower).
- **Pagination**: Cursor-based (`cursor=*` → `meta.next_cursor`), also supports page-based.
- **Page size**: `per_page` (max 100, default 25).
- **Sort**: `sort=field:direction` (e.g., `sort=cited_by_count:desc`).
- **Filters**: `filter=key:value,key:value` — dot notation for nested attributes (e.g., `authorships.author.id:A123`).
- **Search**: `search= query` parameter for full-text search.

## Tech Stack

- **Python 3.12+**, `uv` for dependency management
- **bibliofabric** — framework providing `BaseApiClient`, auth strategies, resource mixins, `ResponseUnwrapper` protocol
- **pydantic v2** + **pydantic-settings** for models and config
- **httpx** for async HTTP (via bibliofabric)
- **pytest** + **pytest-asyncio** + **pytest-httpx** for testing
- **ruff** for linting/formatting
- **ty** for type checking
- **mkdocs-material** + **mkdocstrings** for docs

## Project Structure

```
src/aletheca/
  __init__.py           # Re-exports: client, session, __version__
  client.py             # AlethecaClient (BaseApiClient subclass)
  session.py            # AlethecaSession (user-facing async context manager)
  config.py             # AlethecaSettings (pydantic-settings)
  constants.py          # URLs, defaults, version detection
  endpoints.py          # Filter models with dot-notation aliases
  unwrapper.py          # OpenAlexUnwrapper (ResponseUnwrapper protocol)
  queries.py            # Convenience query functions
  _helpers.py           # Utility functions
  models/
    base.py             # BaseEntity, Meta, EntityType, ApiResponse[T]
    safe_types.py       # SafeList[T], SafeStr
    common.py           # Shared nested types (APCData, Biblio, Location, OpenAccess, etc.)
    ids.py              # Per-entity ID models (WorkIds, AuthorIds, etc.)
    dehydrated.py       # Dehydrated/partial entity models
    work.py             # Work, Authorship, DehydratedSource
    author.py           # Author
    source.py           # Source
    institution.py      # Institution, Repository
    topic.py            # Topic
    publisher.py        # Publisher
    funder.py           # Funder
    award.py            # Award
    keyword.py          # Keyword
  resources/
    _standard.py        # AlethecaResourceClient, StandardResourceClient
    works_client.py     # WorksClient
    authors_client.py   # AuthorsClient
    sources_client.py   # SourcesClient
    institutions_client.py  # InstitutionsClient
    topics_client.py    # TopicsClient
    keywords_client.py  # KeywordsClient
    publishers_client.py    # PublishersClient
    funders_client.py   # FundersClient
    awards_client.py    # AwardsClient
tests/
  _legacy/              # Pre-overhaul suite, excluded from collection (deleted in phase 2)
    conftest.py         # Test fixtures
    test_models.py      # Model validation tests
    test_unwrapper.py   # Response unwrapper tests
    test_helpers.py     # Helper function tests
    resources/          # Per-resource client tests
    test_live_api.py    # Live API smoke tests (live_api marker)
docs/                   # MkDocs documentation
examples/               # Marimo notebook examples
archive/                # Stale plans, reports, one-off analysis (unmaintained)
```

## Development Commands

```bash
uv sync --all-groups                     # Install everything
uv run ruff check --fix                  # Lint
uv run ruff format                       # Format
uv run ty check src                      # Type check
uv run pytest                            # Run tests (legacy suite in tests/_legacy is excluded)
uv build                                 # Build package
uv run mkdocs serve                      # Local docs
```

## Key Patterns & Conventions

- **All I/O is async.** Every resource method is `async`. Use `async with AlethecaSession() as session:` or `async with AlethecaClient() as client:`.
- **Pydantic filter models** use field aliases to map Python names to OpenAlex dot-notation: `authorships_author_id: str | None = Field(None, alias='authorships.author.id')`. Serialization via `model_dump(by_alias=True)` produces the correct filter string.
- **`_serialize_filters()`** override on `AlethecaResourceClient` produces `filter=key:value,key:value` format.
- **Models use `extra="allow"`** everywhere to tolerate API field additions without breaking.
- **Resource clients** all inherit from `StandardResourceClient` (or `AlethecaResourceClient` for works), which combines `SearchableMixin` and `CursorIterableMixin` in its bases; `get()` lives on `AlethecaResourceClient` and delegates to `GettableMixin` after normalizing the entity ID. Each sets `_entity_path`, `_entity_model`, `_search_response_model`.
- **SafeList/SafeStr** handle API's null → empty coercion pattern: `SafeList` converts `None` → `[]` and strips nulls; `SafeStr` converts `None` → `""`.
- **Lazy imports** in `client.py`, `session.py`, `queries.py` avoid circular imports. Ruff `PLC0415` is suppressed for these files.

## Known Issues & Gaps

- **Missing convenience filters**: The `select`, `group_by`, `sample`/`seed` parameters need resource-level methods, not framework changes.
- **Filter model completeness**: Filter models cover the most common filters but not every possible filter. OpenAlex supports many filters; the `extra="allow"` config means users can pass any filter as a dict.
- **Test suite**: The pre-overhaul suite sits in `tests/_legacy`, excluded from collection; phase 2 replaces it with a new suite. Live API smoke tests (`test_live_api.py`) carry the `live_api` marker and are deselected by default.
