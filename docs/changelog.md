# Changelog
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
