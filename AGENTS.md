# Aletheca — Project Guide

Aletheca is an async Python client for the OpenAlex API, built on bibliofabric 0.6. Published on PyPI as `aletheca`; status alpha.

## Architecture

One generic framework layer (bibliofabric) plus an OpenAlex-specific overlay:

```
AlethecaClient               # client.py: BaseApiClient subclass, auth resolution, extra endpoints
 ├─ works/authors/.../awards # resources/*.py: ResourceClient subclasses (cached_property)
 └─ autocomplete(), rate_limit()
```

| File(s) | Role |
|---|---|
| `client.py` | `AlethecaClient(BaseApiClient)`. Resolves credentials (explicit `api_key` > `ALETHECA_API_KEY`/legacy alias env), picks `QueryParameterAuth` (default `?api_key=`) or `StaticTokenAuth` (`auth_scheme="bearer"`), re-raises keyless 401s with an actionable message, and vetoes retries for 429s with `reason: "daily_budget"` in `is_retryable()`. Adds `autocomplete()` and `rate_limit()`. |
| `dialect.py` | `OPENALEX_DIALECT` (per-page/cursor/sort/search/select names) and `OpenAlexResourceClient`: single `filter=` serialization with `\|`-joined OR groups (cap 100, `MAX_OR_VALUES`), DOI normalization, `iterate` default `per-page=100`, `count()` with `select=id`. |
| `resources/*.py` | One client per endpoint (`path`, `model`). `works.py` adds corpus controls, `sample`, `group_by`, `search_scoped`, `citing`/`referenced`, `batch_get_by_doi`. |
| `filters.py` | Pydantic filter models; dot-notation aliases, `extra="allow"`. Deprecated/paid filters deliberately absent. |
| `unwrapper.py` | `OpenAlexUnwrapper`: `meta.count`/`meta.next_cursor`, flattens `meta` into `Page.meta`, keeps envelope extras (e.g. `group_by` buckets). |
| `config.py` | `AlethecaSettings(BaseApiSettings)`, env prefix `ALETHECA_`, `.env` support, `get_settings()` cached. Limiter defaults (10 req/s, concurrency 5) applied in the client because `ty` rejects mutable attribute overrides. |
| `_helpers.py` | `reconstruct_abstract` (inverted index → text). |
| `models/` | Pydantic v2 entity models, `extra="allow"`, SafeList/SafeStr from bibliofabric. |

## Conventions

- Base URL `https://api.openalex.org`. Auth: `api_key` query param (default) or Bearer.
- Cursor paging: `cursor=*` start, `meta.next_cursor` advance. `per-page` max 100; default 25 for `search()`, 100 for `iterate()`.
- Filters: `filter=k:v,k2:v2`; list values join with `|` (max 100); booleans lowercase; DOIs normalized.
- No sessions, no loguru: stdlib logging throughout.

## Development

```bash
uv sync --all-groups      # install
uv run ruff check         # lint (also covers tests, examples)
uv run ruff format        # format
uv run ty check src       # types
uv run pytest             # offline suite (pytest-httpx); live_api tests deselected
uv run pytest -m live_api # live smoke tests; needs ALETHECA_API_KEY
uv run mkdocs build --strict
```

## Testing

`tests/` uses pytest-httpx: responses registered with `add_response(json=...)` without URLs (the `api_key` auth param breaks URL matchers); assert outgoing shape via `httpx_mock.get_requests()`. Real payload fixtures live in `tests/fixtures/` (trimmed from `bibliofabric-family-review/phase2/probes/openalex/`). `tests/test_live_api.py` carries the `live_api` marker and one smoke test per resource.

## Known gaps

- Filter models cover common filters; `extra="allow"` dicts cover the rest.
- Per-operation page-size defaults (25 search / 100 iterate) live in `OpenAlexResourceClient.iterate` because the frozen `QueryDialect` has no `default_iterate_page_size` field.
