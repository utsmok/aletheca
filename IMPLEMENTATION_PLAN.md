# Syntheca (OpenAlex) Implementation Plan

> **Goal**: Bring syntheca up to the quality and completeness of AIREloom, using bibliofabric as the shared base.

## Executive Summary

Syntheca (currently `aletheca`) is a stub: only `entities.py` has substance (~823 lines of dacite dataclasses). Everything else is a docstring stub. The plan is to:

1. **Delete dead code** and restructure as a bibliofabric downstream library
2. **Migrate entities from dacite dataclasses → Pydantic v2 models** (matching bibliofabric/AIREloom)
3. **Implement the full bibliofabric integration layer** (client, config, unwrapper, resources, endpoints)
4. **Mirror AIREloom's project infrastructure** (CI/CD, pre-commit, tests, docs, examples)

> **Note**: All bibliofabric gaps identified in the original plan (§5.1–5.4) have been resolved in bibliofabric v0.3.2. This plan now uses the new hooks directly.

---

## Phase 0: Repository Restructure & Cleanup

### 0.1 Rename package from `aletheca` to `syntheca`
- Rename `src/aletheca/` → `src/syntheca/`
- Update `pyproject.toml` name, build targets, all imports
- Update all references in README, copilot-instructions, marimo checks

### 0.2 Delete dead/stub code
- **Delete** `src/aletheca/api.py` (docstring-only stub — replaced by bibliofabric `BaseApiClient`)
- **Delete** `src/aletheca/endpoints.py` (docstring-only stub — replaced by Pydantic filter models)
- **Delete** `src/aletheca/utils.py` (4 ellipsis-bodies — reimplement if needed after migration)
- **Delete** `src/aletheca/config.py` (two unwired plain classes — replaced by `BaseApiSettings` subclass)
- **Keep but heavily revise** `src/aletheca/entities.py` (rewrite as Pydantic models, see Phase 2)
- **Delete** `marimo_checks/__marimo__/session/` (1.8MB session cache — add to `.gitignore`)

### 0.3 Update `pyproject.toml`
- **Remove** dependencies not needed with bibliofabric: `dacite`, `polars` (move to optional `[analysis]`)
- **Add** `bibliofabric>=0.3.2,<0.4.0` as sole runtime dependency (brings httpx, pydantic, pydantic-settings, tenacity, cachetools, loguru transitively)
- **Add** dev dependencies matching AIREloom: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpx`, `python-dotenv`
- **Add** docs group: `mkdocs~=1.6.0`, `mkdocs-material~=9.5.0`, `mkdocstrings[python]`
- **Add** lint group: `ruff>=0.8.0`
- **Change** build backend from `uv_build` to `hatchling` (consistency with AIREloom/bibliofabric)
- **Add** `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`, `[tool.pytest.ini_options]` sections matching AIREloom's config

### 0.4 Update `.gitignore`
- Add `.marimo/`, `__marimo__/`, `*.session`, `.env`, `.coverage`, `htmlcov/`, `.pytest_cache/`, `site/`

### 0.5 Update `.github/copilot-instructions.md`
- Rewrite to reflect bibliofabric-based architecture, Pydantic models, async-only patterns

### 0.6 Update marimo check notebook
- `marimo_checks/check_entity_dataclasses.py` contains a full duplicate of all dataclasses. After Phase 2, update to import from the package instead of duplicating.

---

## Phase 1: Bibliofabric Integration Layer

### 1.1 Constants module (`src/syntheca/constants.py`)
Mirror AIREloom's pattern:
```python
OPENALEX_API_BASE_URL = "https://api.openalex.org"
OPENALEX_CONTENT_BASE_URL = "https://content.openalex.org"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
DEFAULT_PAGE_SIZE = 25       # OpenAlex default
ITERATE_PAGE_SIZE = 100      # Max for efficient cursor iteration
DEFAULT_USER_AGENT = f"syntheca/{__version__}"
```
- Version via `importlib.metadata` (same as AIREloom)

### 1.2 Config module (`src/syntheca/config.py`)
```python
class SynthecaSettings(BaseApiSettings):
    model_config = SettingsConfigDict(
        env_prefix="SYNTHECA_",
        env_file=(".env", "secrets.env"),
        case_sensitive=False,
        extra="ignore",
    )
    user_agent: str = Field(default=DEFAULT_USER_AGENT)
    openalex_api_key: str | None = Field(default=None, description="OpenAlex API key")
```
- Cached via `@lru_cache` factory
- Only needs `api_key` — OpenAlex doesn't use OAuth2

### 1.3 Auth strategy — uses `QueryParameterAuth` from bibliofabric

OpenAlex authenticates via `?api_key=XXX` as a query parameter. Bibliofabric v0.3.2 provides `QueryParameterAuth` for exactly this:

```python
from bibliofabric import QueryParameterAuth

auth = QueryParameterAuth(key_name="api_key", key_value=settings.openalex_api_key)
```

No workarounds or pre-request hooks needed.

### 1.4 Response Unwrapper (`src/syntheca/unwrapper.py`)
```python
class OpenAlexUnwrapper(ResponseUnwrapper):
    def unwrap_results(self, response_json: dict) -> list[dict]:
        return response_json.get("results", [])
    
    def unwrap_single_item(self, response_json: dict) -> dict:
        return response_json  # Singleton GET returns the entity directly
    
    def get_next_page_token(self, response_json: dict) -> str | None:
        return response_json.get("meta", {}).get("next_cursor")
    
    def get_total_results(self, response_json: dict) -> int | None:
        return response_json.get("meta", {}).get("count")
```

### 1.5 Client (`src/syntheca/client.py`)
```python
class SynthecaClient(BaseApiClient):
    """Async client for the OpenAlex API."""
    
    def __init__(self, settings=None, api_key=None, ...):
        # Resolve auth using QueryParameterAuth
        # Initialize all resource clients as properties
```
- Properties for each resource: `works`, `authors`, `sources`, `institutions`, `topics`, `keywords`, `publishers`, `funders`, `awards`, `domains`, `fields`, `subfields`, `sdgs`, `countries`

### 1.6 Session (`src/syntheca/session.py`)
Thin async context manager wrapping `SynthecaClient`, same pattern as `AireloomSession`:
```python
class SynthecaSession:
    async def __aenter__(self): ...
    async def __aexit__(self): ...
    def __getattr__(self, name): ...  # delegate to client
    @property
    def queries(self): ...  # accessor for convenience query functions
```

---

## Phase 2: Entity Models (Pydantic v2)

This is the largest phase. Migrate all ~50 dataclasses from `entities.py` to Pydantic v2 models, organized by entity type.

### 2.1 Module structure (`src/syntheca/models/`)
```
models/
  __init__.py
  base.py              # BaseEntity, ApiResponse[T], Meta
  ids.py               # WorkIds, AuthorIds, SourceIds, etc.
  dehydrated.py        # DehydratedAuthor, DehydratedInstitution, etc.
  work.py              # Work + nested types (Authorship, Location, Biblio, etc.)
  author.py            # Author + Affiliation
  source.py            # Source + Repository
  institution.py       # Institution + Geo, Role, International
  topic.py             # Topic, Domain, Field, Subfield, TopicMinimal
  publisher.py         # Publisher
  funder.py            # Funder, DehydratedFunder
  award.py             # Award (NEW — not in current entities.py)
  keyword.py           # Keyword, DehydratedKeyword
  concept.py           # Concept (DEPRECATED — keep for migration compat)
  common.py            # SummaryStats, APCData, APCEntry, OpenAccess, YearCount, etc.
  safe_types.py        # SafeList, SafeStr (copied from AIREloom pattern)
```

### 2.2 Key design decisions

1. **All models use `extra="allow"`** for forward compatibility (matches AIREloom pattern)
2. **`SafeList[T]` and `SafeStr`** annotated types for None-safe traversal (copy from AIREloom)
3. **`SafeModel` pattern** for nested models that should never be None
4. **`summary_stats` field**: Use Pydantic `alias` to map `2yr_mean_citedness` → `two_yr_mean_citedness` (this was the unsolvable problem with dacite — trivial with Pydantic)
5. **`BaseEntity`**: Common fields (`id`, `display_name`, `works_count`, `cited_by_count`)
6. **`ApiResponse[T]`**: Generic envelope with `Meta` + `results: list[T]`
7. **Dehydrated objects**: Model as-is from the API (partial entity fields)

### 2.3 New entities to add (not in current entities.py)
Based on the current OpenAlex API docs:
- **Award** entity (funders → awards link, new endpoint)
- **Domain, Field, Subfield** as separate top-level entities (separate endpoints)
- **Country, Continent, Language** entities (enum/list endpoints)

### 2.4 Entities to mark as deprecated
- **Concept** → replaced by Topic (keep model but add deprecation warning)
- All `x_concepts` fields → replaced by `topics`

### 2.5 Response models
```python
class Meta(BaseModel):
    count: int | None = None
    db_response_time_ms: float | None = None
    page: int | None = None
    per_page: int | None = None
    next_cursor: str | None = None
    groups_count: int | None = None
    cost_usd: float | None = None

class ApiResponse[T: BaseEntity](BaseModel):
    meta: Meta = Field(default_factory=Meta)
    results: list[T] = Field(default_factory=list)
    group_by: list[dict] | None = None
```

---

## Phase 3: Endpoints, Filters & OpenAlex Integration

### 3.1 Endpoint definitions (`src/syntheca/endpoints.py`)
Pydantic filter models per endpoint, matching AIREloom's pattern:

```python
WORKS = "works"
AUTHORS = "authors"
SOURCES = "sources"
# ... etc

class WorksFilters(BaseModel):
    """Filter model for Works endpoint.
    
    OpenAlex filter syntax is a single 'filter' query param with colon-separated
    key:value pairs, comma-joined for AND, pipe-joined for OR.
    This model's fields map to filter keys.
    """
    publication_year: int | None = None
    publication_year_range: str | None = None  # "2020-2024"
    authorships_author_id: str | None = None  # OpenAlex ID or pipe-separated
    # ... ~150 filterable fields
    model_config = ConfigDict(extra="forbid")
```

### 3.2 OpenAlex filter serialization — override `_serialize_filters()`

Bibliofabric v0.3.2 provides `_serialize_filters()` on `BaseResourceClient`. The default dumps Pydantic filter models as individual query params (OpenAIRE style). Syntheca overrides it to produce OpenAlex's single `filter=key:value,key:value` string:

```python
class SynthecaResourceClient(BaseResourceClient):
    """Base for all OpenAlex resource clients."""
    
    _param_page_size: str = "per_page"   # OpenAlex uses per_page, not pageSize
    _param_sort: str = "sort"            # OpenAlex uses sort, not sortBy
    
    def _serialize_filters(
        self, filters: BaseModel | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Serialize filters into OpenAlex's single `filter` query parameter.
        
        OpenAlex syntax: filter=publication_year:2024,is_oa:true
        OR within a field: filter=authorships.author.id:A123|A456
        """
        if filters is None:
            return {}
        
        if isinstance(filters, BaseModel):
            filter_dict = filters.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(filters, dict):
            filter_dict = dict(filters)
        else:
            raise BibliofabricError(
                f"filters must be a Pydantic model or dictionary, got {type(filters)}"
            )
        
        if not filter_dict:
            return {}
        
        # Build the OpenAlex filter string: key:value,key:value
        parts = []
        for key, value in filter_dict.items():
            parts.append(f"{key}:{value}")
        
        return {"filter": ",".join(parts)}
```

This is a single override in one base class — all resource clients inherit it automatically.

### 3.3 Parameter name customization — class attributes

Bibliofabric v0.3.2 exposes parameter names as class attributes on `BaseResourceClient` with sensible defaults. Syntheca overrides only the two that differ:

```python
class SynthecaResourceClient(BaseResourceClient):
    _param_page_size: str = "per_page"
    _param_sort: str = "sort"
    # _param_page = "page"      # already matches default
    # _param_cursor = "cursor"  # already matches default
    # _param_id = "id"          # already matches default
    # _param_search = "search"  # already matches default
```

No mixins need to be overridden — they all read from `self._param_*`.

### 3.4 Sort parameter format

OpenAlex uses `sort=field:direction` (e.g., `sort=cited_by_count:desc`).
The `_param_sort` attribute handles the name (`sort` vs `sortBy`). The format (`field:direction` vs `field direction`) is controlled by what callers pass to `sort_by`:

```python
# Caller passes OpenAlex-formatted sort string
await client.works.iterate(sort_by="cited_by_count:desc")
```

No additional bibliofabric hooks needed — the sort string is opaque to the mixin.

### 3.5 Search parameter — directly supported

Bibliofabric v0.3.2 adds `search: str | None = None` to all mixin methods (`search()`, `iterate()`, `collect()`, `count()`). OpenAlex's top-level `search` query param is used directly:

```python
# Full-text search
results = await client.works.search(search="machine learning", page_size=25)

# Combined with filters
results = await client.works.iterate(
    filters=WorksFilters(publication_year=2024),
    search="transformer architecture"
)

# Convenience
count = await client.works.count(search="quantum computing")
```

The `_param_search = "search"` default already matches OpenAlex — no override needed.

### 3.6 Select parameter

OpenAlex uses `select=id,title,doi` to limit returned fields. Not built into bibliofabric mixins. Add as a resource-client-level method:

```python
class WorksClient(SynthecaResourceClient, GettableMixin, SearchableMixin, CursorIterableMixin):
    async def select(self, fields: list[str], **kwargs) -> AsyncIterator[Any]:
        """Fetch only specified fields."""
        params = {**kwargs, "select": ",".join(fields)}
        # ... custom iterate with select param
```

### 3.7 Group_by parameter

OpenAlex uses `group_by=field` for aggregation. Add as resource-client methods:

```python
async def group_by(self, field: str, **kwargs) -> list[dict]:
    """Group results by a field. Returns aggregation buckets."""
```

### 3.8 Sample/seed parameters

OpenAlex supports `sample=N&seed=N` for random sampling. Add as resource-level methods:

```python
async def sample(self, n: int, seed: int | None = None) -> list[Work]:
    """Get a random sample of works."""
```

---

## Phase 4: Resource Clients

### 4.1 Syntheca resource client base

All syntheca resource clients inherit from `SynthecaResourceClient` which sets the OpenAlex-specific param names and filter serialization:

```python
class SynthecaResourceClient(BaseResourceClient):
    """Base for all OpenAlex resource clients."""
    _param_page_size: str = "per_page"
    _param_sort: str = "sort"
    
    def _serialize_filters(self, filters):
        # ... OpenAlex filter string serialization (see §3.2)
```

### 4.2 Standard resource client pattern

For the 8 core entities that support GET/search/iterate:
```python
class WorksClient(GettableMixin, SearchableMixin, CursorIterableMixin, SynthecaResourceClient):
    _entity_path = "works"
    _entity_model = Work
    _search_response_model = WorkResponse
    _supports_direct_get = True  # OpenAlex supports GET /works/{id}
```

### 4.3 Resource clients needed (22 endpoints → ~16 resource clients)

**Core (full CRUD + cursor iteration)**:
1. `WorksClient` — `/works` (19 types, ~270M records)
2. `AuthorsClient` — `/authors`
3. `SourcesClient` — `/sources`
4. `InstitutionsClient` — `/institutions`
5. `TopicsClient` — `/topics`
6. `KeywordsClient` — `/keywords`
7. `PublishersClient` — `/publishers`
8. `FundersClient` — `/funders`

**Supporting (GET + search, possibly cursor)**:
9. `AwardsClient` — `/awards` (new endpoint)
10. `DomainsClient` — `/domains` (4 records, mostly static)
11. `FieldsClient` — `/fields`
12. `SubfieldsClient` — `/subfields`
13. `SdgsClient` — `/sdgs` (17 records)
14. `CountriesClient` — `/countries`

**Enum-only (GET list, no search/filter)**:
15. `WorkTypesClient` — `/work-types`
16. `SourceTypesClient` — `/source-types`
17. `InstitutionTypesClient` — `/institution-types`
18. `LicensesClient` — `/licenses`

**Special endpoints**:
19. `AutocompleteClient` — `/autocomplete/{entity_type}`
20. `RateLimitClient` — `/rate-limit`

### 4.4 WorksClient special features
- External ID lookup: `/works/doi:10.1234/x`, `/works/pmid:12345`
- `sample()` / `sample_with_seed()` methods
- `group_by()` method for aggregation
- `select()` for field selection
- `search()` for full-text search (separate from filter)

---

## Phase 5: Convenience Queries (`src/syntheca/queries.py`)

Mirror AIREloom's `_QueryAccessor` pattern:

```python
async def works_by_author(session, author_name, limit=None) -> list[Work]:
    """Two-step: search author → get works by ID."""
    authors = await session.authors.search(search=author_name, page_size=1)
    if not authors.results:
        return []
    author_id = authors.results[0].id
    return await session.works.collect(
        filters={"authorships.author.id": author_id},
        limit=limit
    )

async def works_by_institution(session, institution_name, limit=None) -> list[Work]:
async def works_by_doi(session, dois: list[str]) -> list[Work]:
async def citing_works(session, work_id) -> list[Work]:
async def referenced_works(session, work_id) -> list[Work]:
async def related_topics(session, entity_id) -> list[Topic]:
```

---

## Phase 6: Helpers & Utilities (`src/syntheca/_helpers.py`)

- DOI normalization (`doi.org/` prefix handling)
- OpenAlex ID parsing (`https://openalex.org/W123` → `W123`)
- ID type detection (DOI, PMID, ORCID, ISSN, ROR, etc.)
- Inverted abstract reconstruction
- External ID resolution helpers

---

## Phase 7: Project Infrastructure

### 7.1 CI/CD (`.github/workflows/python-ci.yml`)
Copy AIREloom's CI:
- Python 3.12 + 3.13 matrix
- `uv sync --all-groups --all-extras`
- `ruff check src/`
- `ty check src/`
- `pytest --cov=syntheca --cov-fail-under=95 tests/`
- `uv build`
- Docs deploy on push to main
- Publish on tag

### 7.2 Pre-commit hooks (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.12
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        files: ^src/
```

### 7.3 AGENTS.md
Write comprehensive project guide matching AIREloom's AGENTS.md format:
- Architecture diagram
- Key layers table
- API version routing
- Auth
- Tech stack
- Project structure
- Development commands
- Key patterns & conventions
- Known issues & gaps

### 7.4 Tests (`tests/`)
Structure matching AIREloom:
```
tests/
  conftest.py              # dotenv loading, fixtures
  test_session.py          # Integration tests via mocked HTTP
  test_auth.py             # Auth/api-key injection tests
  test_config.py           # Config/env override tests
  test_unwrapper.py        # Response unwrapper unit tests
  test_client.py           # Client unit tests
  test_models.py           # Pydantic model validator tests
  test_queries.py          # Convenience query tests
  test_helpers.py          # Helper function tests
  resources/               # Per-resource client tests
    test_works_client.py
    test_authors_client.py
    ...
```
- Use `pytest-httpx` for mocking (same as bibliofabric/AIREloom)
- `pytest.mark.live_api` for real API tests (skipped by default)
- 95% coverage threshold

### 7.5 Documentation (`docs/`)
MkDocs + mkdocs-material:
- Getting started, installation, authentication
- Usage basics
- Per-endpoint docs
- Advanced: caching, rate limiting, hooks, error handling
- API reference (auto-generated via mkdocstrings)
- Contributing guide
- Changelog

### 7.6 Examples (`examples/`)
Marimo notebooks (matching AIREloom's approach):
- Basic usage
- Works filtering and search
- Author discovery
- Institution analysis
- Topic exploration
- Advanced filtering
- Iterator helpers
- Convenience queries

---

## Phase 8: Documentation & Package

### 8.1 README.md
- Badges (CI, coverage, PyPI, Python versions)
- Quick start example
- Feature list
- Installation instructions
- Development setup
- Link to docs

### 8.2 `__init__.py` public API
```python
from .client import SynthecaClient
from .session import SynthecaSession
from .models import (Work, Author, Source, Institution, Topic, ...)
from .constants import __version__
from bibliofabric.exceptions import (APIError, NotFoundError, RateLimitError, ...)
```

---

## §5: Bibliofabric Gaps — Status Update

### 5.1 ✅ RESOLVED: Query Parameter Auth Strategy
**Status**: `QueryParameterAuth` added to bibliofabric v0.3.2 in `auth.py`, exported in `__init__.py`.

**Syntheca usage**:
```python
from bibliofabric import QueryParameterAuth
auth = QueryParameterAuth(key_name="api_key", key_value=settings.openalex_api_key)
```

### 5.2 ✅ RESOLVED: Filter Serialization Hook
**Status**: `_serialize_filters()` method added to `BaseResourceClient` in bibliofabric v0.3.2. All 3 mixins (`SearchableMixin`, `CursorIterableMixin`, `PageIterableMixin`) call it instead of inline serialization.

**Syntheca usage**: Override in `SynthecaResourceClient` to produce OpenAlex's `filter=key:value,key:value` string (see §3.2).

### 5.3 ✅ RESOLVED: Parameter Name Customization
**Status**: Class attributes `_param_page`, `_param_page_size`, `_param_sort`, `_param_cursor`, `_param_id`, `_param_search` added to `BaseResourceClient`. All mixins use them.

**Syntheca usage**: Override `_param_page_size="per_page"` and `_param_sort="sort"` in `SynthecaResourceClient` (see §3.3).

### 5.4 ✅ RESOLVED: Search Parameter Support
**Status**: `search: str | None = None` parameter added to `search()`, `iterate()` (both cursor and page), `collect()`, and `count()` in bibliofabric v0.3.2.

**Syntheca usage**: Pass `search="query"` directly to any mixin method (see §3.5).

### 5.5 Minor gaps (not blocking, resource-level solutions)
- **`select` parameter**: OpenAlex field selection. Add as resource-client method (see §3.6).
- **`group_by` parameter**: Aggregation endpoint. Add as resource-client method (see §3.7).
- **`sample`/`seed` parameters**: Random sampling. Add as resource-client methods (see §3.8).

---

## §6: Implementation Order (Recommended)

1. **Phase 0** — Restructure & cleanup (immediate, no dependencies)
2. **Phase 1** — Bibliofabric integration layer (constants, config, unwrapper, client skeleton, session)
3. **Phase 2** — Pydantic models (migrate entities.py → models/)
4. **Phase 3** — Endpoints, filters & OpenAlex integration (no longer blocked on upstream)
5. **Phase 4** — Resource clients (requires Phase 1+2+3)
6. **Phase 5** — Convenience queries
7. **Phase 6** — Helpers
8. **Phase 7** — Infrastructure (CI, tests, docs, pre-commit) — can start early
9. **Phase 8** — Polish (README, __init__.py, examples)

Phases 7 and 0 can proceed in parallel. Phase 2 is the largest single chunk of work. Phases 3–4 are no longer blocked on upstream bibliofabric changes.

---

## §7: Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| ~~Bibliofabric parameter naming gap~~ | ~~High~~ **Resolved** | Override class attributes in `SynthecaResourceClient` |
| ~50 dataclasses → Pydantic migration errors | Medium | Incremental migration with tests; use `extra="allow"` for safety |
| OpenAlex filter syntax too complex for generic serialization | Medium | Custom `_serialize_filters()` override in `SynthecaResourceClient` |
| Deprecated entities (Concept) removal breaks users | Low | Keep with deprecation warning |
| OpenAlex API changes underfoot | Low | `extra="allow"` on all models provides buffer |
