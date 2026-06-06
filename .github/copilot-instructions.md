## Syntheca — Copilot instructions

Be concise and make edits that match existing styles and typing. Use these repository-specific notes to make PR-ready changes.

This project is a Python library to interact with the OpenAlex API, built on top of the **bibliofabric** framework (shared with AIREloom for OpenAIRE). It provides tools for data retrieval, modeling, and analysis of scholarly entities.

### Architecture

- **bibliofabric** provides: `BaseApiClient`, `BaseResourceClient`, mixins (`GettableMixin`, `SearchableMixin`, `CursorIterableMixin`, `PageIterableMixin`), `ResponseUnwrapper` protocol, `AuthStrategy` protocol, `BaseApiSettings`, TTLCache + tenacity
- **syntheca** provides: OpenAlex-specific models, resource clients, config, unwrapper, session, queries

### Project layout

```
src/syntheca/
  __init__.py          # Public API
  constants.py         # API URLs, defaults, version
  config.py            # SynthecaSettings (pydantic-settings)
  unwrapper.py         # OpenAlexUnwrapper (ResponseUnwrapper impl)
  client.py            # SynthecaClient (BaseApiClient impl)
  session.py           # SynthecaSession (async context manager)
  endpoints.py         # Pydantic filter models per endpoint
  resources/           # Resource clients (mixin-based)
  models/              # Pydantic v2 entity models
  queries.py           # Convenience query functions
  _helpers.py          # DOI normalization, ID parsing, etc.
  entities.py          # LEGACY dacite dataclasses (being migrated to models/)
  py.typed             # PEP 561 marker
```

### Key patterns

- **Pydantic v2 models**: All entity models use `extra="allow"` for forward compatibility
- **SafeList[T] / SafeStr**: Annotated types for None-safe traversal (see `models/safe_types.py`)
- **Async-only**: All API interactions are async (httpx)
- **Mixin-based resource clients**: Inherit from `SynthecaResourceClient` + bibliofabric mixins
- **Filter serialization**: Override `_serialize_filters()` for OpenAlex `filter=key:value` syntax
- **Param name overrides**: `_param_page_size="per_page"`, `_param_sort="sort"`
- **Auth**: Uses `QueryParameterAuth` from bibliofabric (`?api_key=XXX`)
- **Cursor pagination**: OpenAlex supports cursor-based pagination via `meta.next_cursor`

### Developer workflows

- Environment/deps: the project uses `uv` (see `pyproject.toml`).
- **NEVER** use `python`, `pip`, or `venv` directly; always use `uv`:
  - `uv run main.py` instead of `python main.py`
  - `uv add package` instead of `pip install package`
  - `uv sync --all-groups` to install all dependency groups
- Tests: `uv run pytest` (see `tests/`)
- Linting: `uv run ruff check src/` and `uv run ruff format src/`
- Type checking: `uvx ty check src/` (uses `ty`, NOT mypy or pyright)
  - Use `# ty: ignore[error-code]` for suppressions

### Formatting and typing

- The package exposes `py.typed` (PEP 561); preserve type annotations
- Dataclasses/models should be instantiated with keyword arguments
- Use `ruff` for linting and formatting
- Field names should mirror the OpenAlex API exactly
- For non-Pythonic API names (e.g., `2yr_mean_citedness`), use Pydantic `alias`
