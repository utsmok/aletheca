# Changelog

All notable changes to Aletheca are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 0.4.0

Rewritten onto bibliofabric 0.6 (one generic `ResourceClient` + `QueryDialect`
per API, `Page[E]` results, stdlib logging, no loguru, no sessions). Breaking
changes are listed under each heading.

### Removed

- `AlethecaSession` and `session.queries.*`; use `AlethecaClient` and the
  resource methods (`works.citing()`, `works.referenced()`,
  `works.batch_get_by_doi()`). Only `ea-cli-refactor/scripts/litsearch.py`
  used the session class.
- `AlethecaClient` copy-pasted lazy properties replaced by typed
  `functools.cached_property` resources (`client.works` is now `WorksClient`).
- `aletheca.constants` (dead constants), `_batch`/duplicated batch code,
  and loguru usage (stdlib `logging` throughout).
- Envelope models `ApiResponse`, `Meta`, and `models/safe_types.py` shim;
  `search()` returns `bibliofabric.Page[E]` (`page.results`, `page.total`,
  `page.next_cursor`, `page.meta`). `Page.meta` carries OpenAlex `meta`
  flattened (`count`, `cost_usd`, `x_query`, `notice`) plus envelope extras
  such as `group_by` buckets.
- All polite-pool/`mailto` claims from docs, README, and settings: OpenAlex
  removed the polite pool in February 2026 (`mailto` is ignored). A free API
  key is required for cursor paging past the first page.

### Changed

- Settings: `ALETHECA_API_KEY` is the canonical env name
  (`ALETHECA_OPENALEX_API_KEY` still accepted as an alias, and the
  `openalex_api_key=` constructor keyword keeps working for consumers). New
  `auth_scheme` setting chooses `query` (`?api_key=`, default) or `bearer`
  (`Authorization: Bearer`). Limiter defaults are now 10 req/s and
  concurrency 5 (env-overridable).
- Query dialect: `per-page` max 100 (never emits 200), default 25 for
  `search()` and 100 for `iterate()`; cursor paging; `search` and `select`
  parameters supported on every resource.
- Filters serialize to `filter=k:v,k2:v2`; list values become `|`-joined OR
  groups with the documented 100-value cap enforced client-side (batch size
  raised from 50 to 100, halving `batch_get` request counts). DOIs are
  normalized (`https://doi.org/` prefixes stripped, lowercased) before they
  enter OR filters or batch queries.
- `count()` sends `per-page=1` with `select=id` (minimal payload per count).
- Retry policy: a 429 whose body carries `reason: "daily_budget"` is not
  retried (it cannot succeed before the UTC midnight reset); other 429s and
  5xx retry with `Retry-After` honored as before.
- Keyless cursor paging that hits 401 raises `AuthError` with an actionable
  message pointing at `ALETHECA_API_KEY` instead of the opaque upstream body.
- `batch_get(ids, field=..., batch_size=...)` now comes from bibliofabric:
  concurrent chunks, results keyed by normalized identifiers (works without
  the requested field fall back to their OpenAlex id as key). The old
  `key_fn` parameter is gone.

### Added

- Works-level helpers: `group_by(field, filters=...)` returning typed
  `GroupByBucket` objects (nested `groups` for multi-field group-by, cursor
  paging supported), `sample(n, seed=...)` (reproducible, max 10,000),
  `search(corpus=..., include_parts=..., include_pulled=...)`,
  `search_scoped(text, scope=...)` covering `search.title`,
  `search.title_and_abstract`, `search.title_abstract_keywords`,
  `search.exact`, and `search.semantic`, plus `citing()` and `referenced()`
  citation-graph helpers with bounded defaults.
- New endpoints: `client.autocomplete(query, entity_type=...)` (free
  typeahead, typed `AutocompleteResult`) and `client.rate_limit()` (typed
  `RateLimitStatus` with remaining budget; the echoed key is never stored).
- `select=` on searches cuts payload size.
- `client.locations` (`/locations` per-copy index, typed `LocationRecord`;
  `get`/`search`/`iterate`; namespaced ids such as `doi:...` stay intact
  because the single route 404s on bare DOIs).
- `client.links` (`/links` citation-graph edges, typed `Link` with
  `relationship` labels) with `origin(work_id)` and `target(work_id)`
  helpers.
- `works.search(rerank=True)` sends `rerank=true` (top-100 reranking for
  relevance-sorted searches, +10 credits); whether it applied is readable
  from `page.meta["reranked"]`.
- `works.oa_pdf_urls(doi_or_id)` returns the work's downloadable PDF URLs,
  best OA copy first (`[]` when none).

### Deprecated filters removed (OX-14)

- `WorksFilters.concepts_id`, `AuthorsFilters.x_concepts_id`,
  `SourcesFilters.x_concepts_id`: deprecated aliases of `topics.id`.
- `WorksFilters.is_xpac` and `include_xpac`: legacy corpus controls that
  400 when combined with `corpus=`; use `corpus=` instead.
- `default_search` on every filter model: alias of `fulltext.search`.
- `WorksFilters` sync filters (`from/to_created_date`,
  `from/to_updated_date`): paid (Member+/Partner; free accounts get 403).
- `SourcesFilters.is_in_jstage*`: no longer returned or documented upstream.

### Migration from 0.3

| 0.3 call | 0.4 call |
|---|---|
| `AlethecaSession()` / `session.works` | `AlethecaClient()` / `client.works` |
| `session.queries.works_by_doi(dois)` | `client.works.batch_get_by_doi(dois)` → `dict[doi, Work]` |
| `session.queries.citing_works(id)` | `client.works.citing(id, limit=100)` |
| `session.queries.referenced_works(id)` | `client.works.referenced(id, limit=100)` |
| `session.queries.works_by_author(name)` | `client.authors.search(query=name)` then `client.works.iterate({"authorships.author.id": id})` |
| `session.queries.works_by_institution(name)` | resolve via `client.institutions.search(query=name)`, then filter `authorships.institutions.id` |
| `resp = await works.search(...)` → `resp.meta.count` | `page = await works.search(...)` → `page.total` (or `page.meta["count"]`) |
| `ApiResponse[Work]` type annotation | `bibliofabric.Page[Work]` |
| `WorksFilters(corpus="expansion")` | `works.search(filters, corpus="expansion")` |
| `works.search(filters, search="x")` | `works.search(filters, query="x")` |
| `AlethecaSettings(openalex_api_key=...)` | `AlethecaSettings(api_key=...)` (old keyword still accepted) |
| `client.works.batch_get(ids, field="doi", key_fn=f)` | `client.works.batch_get(ids, field="doi")` (keys are normalized ids; no `key_fn`) |
| `BATCH_GET_SIZE = 50` | `aletheca.dialect.MAX_OR_VALUES = 100` |
| `from aletheca.endpoints import WorksFilters` | `from aletheca.filters import WorksFilters` (also re-exported top-level) |
| `from aletheca.models import Meta` | `page.meta["count"]`, `page.meta["cost_usd"]`, `page.meta["x_query"]` |

## [0.3.0] - 2026-11-16

### Added

- Work part-of fields: `parent_works` (dehydrated parent + `relationship`:
  `volume`, `component`, `data-series`, `part`), `lineage` (own ID first,
  then ancestors nearest first), `child_works_count`, and `is_traditional`
  (OpenAlex's 2026-11-15 "works can now have parts" release)
- `WorksFilters` part-of filters: `has_parent_work`, `parent_works_id`
  (`parent_works.id`), `parent_works_relationship`
  (`parent_works.relationship`), `lineage`, `child_works_count`,
  `is_traditional`
- `WorksFilters` supports the works query parameters `include_parts` and
  `corpus`; `WorksClient` emits them as standalone query parameters instead
  of `filter=` keys (other endpoints keep unknown keys as filters, so a
  stray `corpus` still fails at the API rather than changing the request)

### Fixed

- CI type check green again: resource client `_entity_model`/
  `_search_response_model` annotations widened to `type[BaseModel] | None`
  (ty 0.0.104, what `uvx ty` resolves since September, rejects narrow
  overrides of mutable base attributes) and two `ty: ignore` comments
  updated to the renamed `missing-attribute` rule. Assigned values and
  runtime behavior are unchanged.

## [0.2.2] - 2026-09-05

### Fixed

- `Institution.associated_institutions` accepts any relationship value
  (e.g. `predecessor`), which 3,291 live records carry (#2)
- Paging parameter annotations widened to `str | None` to satisfy
  bibliofabric 0.5's `ResourceClientProtocol` under strict type checking

### Changed

- bibliofabric bumped to `>=0.5.1` (pluggable paging, resumable cursors,
  strict parse modes, opt-in rate pacing)
- Removed dead `ITERATE_PAGE_SIZE` constant, which claimed a per_page max
  of 200 (OpenAlex's documented ceiling is 100) (#1)

### Docs

- Page-size examples and docs reconciled to the documented 100 ceiling.
  Wrong Python kwarg names (`per_page=`, `sort=`) in call examples fixed
  in a docs-only commit on main immediately after tagging
- Dated resolution note on the DOC-1 per_page finding

## [0.2.1] - 2026-09-04

### Fixed

- `get()` normalizes entity IDs, so slug-keyed entities (e.g. keywords like
  `photosynthesis`) resolve instead of returning 404
- `AwardsFilters` aligned with the live API's valid-filter list (previously
  accepted filters that always returned HTTP 400)
- Marimo example notebooks: WASM embedding compatibility and correct
  multi-renderable-cell output

### Docs

- Recorded live-verified OpenAlex quirks (keyword slug IDs, awards filter
  enumeration via 400 bodies)
- Removed stale "awards client not implemented" note from AGENTS.md

## [0.2.0] - 2026-06-07

### Added

- Batch retrieval (`batch_get()`) with auto-generated `batch_get_by_*()`
  convenience methods
- OpenAIRE vs OpenAlex cross-reference analysis report

### Fixed

- Nullable boolean fields in `Location` and `OpenAccess` made optional
- Roborev review findings; examples README code block; mkdocs formatting

## [0.1.0] - 2026-06-06

### Added

- Initial release of Aletheca
- Full async client for the OpenAlex API
- 9 entity models: Work, Author, Source, Institution, Topic, Keyword, Publisher, Funder, Award
- Pydantic v2 models with safe field access (SafeList, SafeStr)
- Filter models with dot-notation alias support for all 9 endpoints
- Convenience query functions (works_by_author, works_by_institution, etc.)
- Cursor-based pagination via bibliofabric mixins
- Iterator helpers: collect(), count(), first()
- Configurable authentication (API key query parameter)
- Comprehensive test suite (104 tests, 98% coverage)
- Live API verification suite
- MkDocs documentation
- Marimo notebook examples

[Unreleased]: https://github.com/utsmok/aletheca/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/utsmok/aletheca/releases/tag/v0.3.0
[0.2.2]: https://github.com/utsmok/aletheca/releases/tag/v0.2.2
[0.2.1]: https://github.com/utsmok/aletheca/releases/tag/v0.2.1
[0.2.0]: https://github.com/utsmok/aletheca/releases/tag/v0.2.0
[0.1.0]: https://github.com/utsmok/aletheca/releases/tag/v0.1.0
