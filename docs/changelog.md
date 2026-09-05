# Changelog

## v0.2.2 (2026-09-05)

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

## v0.2.0 (2026-06-07)

### Added
- Batch retrieval (`batch_get()`) with auto-generated `batch_get_by_*()`
  convenience methods
- OpenAIRE vs OpenAlex cross-reference analysis report

### Fixed
- Nullable boolean fields in `Location` and `OpenAccess` made optional
- Roborev review findings; examples README code block; mkdocs formatting

## v0.2.1 (2026-09-04)

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


## v0.1.0 (2026-06-05)

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
