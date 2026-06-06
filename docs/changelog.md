# Changelog

## v0.1.0 (2026-06-05)

### Added
- Initial release of Syntheca
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
