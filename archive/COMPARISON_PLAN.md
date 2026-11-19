# AIREloom ↔ Aletheca Comparison Plan

**Date:** 2026-06-05
**Repositories:** `~/dev/aletheca/` (aletheca), `~/dev/AIREloom/` (aireloom), `~/dev/bibliofabric/` (shared base)

---

## 1. Structural Overview

| Aspect | Aireloom | Aletheca | Status |
|--------|----------|----------|--------|
| Package lines | 3,924 | 2,494 | aletheca leaner (fewer entities with complex models) |
| Entities | 6 + Scholix + Links | 9 | Different API surfaces |
| Resource clients | 6 + Scholix (custom) | 9 (all standard) | aletheca more uniform |
| Pydantic models | 11 files | 14 files | aletheca has dedicated `ids.py`, `dehydrated.py` |
| Tests | 251 (5 live deselected) | 104 | aletheca under-tested relative to surface area |
| Examples | 11 scripts | 1 script | **aletheca gap** |
| CI | Identical | Identical | ✅ |
| Build system | hatchling | hatchling | ✅ |

---

## 2. Aletheca Gaps (Implement)

### 2.1 [High] Expand Examples

Aireloom has 11 focused examples demonstrating every feature. Aletheca has one.

**Add:**
- `examples/02_filtering_and_search.py` — WorksFilters, AuthorsFilters, etc.
- `examples/03_institution_research.py` — works by institution, topic analysis
- `examples/04_author_discovery.py` — find authors, get their works
- `examples/05_advanced_queries.py` — cursor pagination, select fields, sort
- `examples/06_convenience_queries.py` — session.queries.* functions
- `examples/07_iterator_helpers.py` — collect, count, first from bibliofabric mixins
- `examples/08_safe_types_and_models.py` — SafeList, SafeStr, extra="allow"
- Update `examples/README.md` to describe all examples

### 2.2 [High] Add Ergonomics/Features Documentation

Aireloom has `docs/ergonomics.md` — a dedicated page documenting:
- Safe field access (SafeList, SafeStr)
- Iterator helpers (collect, count, first)
- Convenience query functions

Aletheca has these features (SafeList, SafeStr in models, queries.py, iterator helpers from bibliofabric) but no docs page for them.

**Add `docs/ergonomics.md`** covering:
- Safe types: `SafeList`, `SafeStr` behavior
- Iterator helpers: `collect()`, `count()`, `first()` from bibliofabric mixins
- Convenience queries: `session.queries.works_by_author()`, etc.
- OpenAlex-specific helpers: `normalize_doi()`, `parse_openalex_id()`, `reconstruct_abstract()`
- Add to `mkdocs.yml` nav

### 2.3 [High] Add Changelog Doc

Aireloom has `docs/changelog.md` with versioned entries. Aletheca doesn't.

**Add `docs/changelog.md`** with v0.1.0 entry covering initial release.
Add to `mkdocs.yml` nav.

### 2.4 [Medium] Add Live API Test Module

Aireloom has `tests/test_actual_data.py` with `@pytest.mark.live_api` guard (skipped in CI). Aletheca has `scripts/verify.py` for live verification but no pytest-guarded live tests.
**Add `tests/test_live_api.py`** with:
- `@pytest.mark.live_api` marker (already defined in `pyproject.toml`)
- Basic smoke tests: fetch one of each entity, verify deserialization
- Filter round-trip tests: create filter, query, verify results exist
- Keep minimal — the heavy verification is in `scripts/verify.py`

### 2.5 [Medium] Add Auth Tests

Aireloom has 12 auth tests (`test_auth.py`). Aletheca has none — auth handling is simpler (QueryParameterAuth vs OAuth2) but still deserves coverage.
**Add `tests/test_auth.py`** testing:
- `QueryParameterAuth` adds `api_key` to query params
- `NoAuth` fallback when no key
- Auth strategy override in client constructor

### 2.6 [Medium] Expand Public API Exports

Aireloom re-exports from `__init__.py`:
- All bibliofabric exceptions (APIError, AuthError, etc.)
- Key models (ResearchProduct, Organization, etc.)
- `__version__` from constants

Aletheca only exports `AlethecaClient`, `AlethecaSession`, and `__version__` (via importlib in `__init__.py`).

**Update `src/aletheca/__init__.py`** to also export:
- Key models: `Work`, `Author`, `Source`, `Institution`, `Topic`, `Keyword`, `Publisher`, `Funder`, `Award`
- Common models: `ApiResponse`, `BaseEntity`, `Meta`
- Exceptions from bibliofabric
- `__version__` from constants (consolidate to constants.py like aireloom)

### 2.7 [Medium] Add Marimo-Embedded Example Iframes in Docs

Aireloom embeds interactive marimo notebooks as iframes in docs pages (ergonomics.md). Aletheca has a marimo check notebook but no embedded examples.

**Add iframes** to relevant docs pages (ergonomics.md when created, usage_basics.md).

### 2.8 [Low] Add Computed Properties to Models

Aireloom's models expose computed properties (e.g., `product.doi`, `product.is_open_access`, `person.orcid`). Aletheca models are plain data holders.

**Consider adding** to key models:
- `Work.doi` — extract from `work.doi` (already a field, less needed)
- `Work.publication_year` — already a field
- `Author.orcid` — already a field
- `Work.reconstruct_abstract()` — could be a computed property calling `_helpers.reconstruct_abstract`

This is less impactful for aletheca since OpenAlex returns flatter structures than OpenAIRE. **Defer unless users request it.**

---

## 3. Aireloom Gaps (Do NOT Implement — for aireloom agent)

> These findings are duplicated in `~/dev/AIREloom/AIRELOOM_IMPROVEMENT_PLAN.md` for the aireloom agent to implement.

### 3.1 [High] Add `py.typed` PEP 561 Marker

Aletheca has `src/aletheca/py.typed`. Aireloom doesn't. Both claim `Typing :: Typed` classifier.

**Add `src/aireloom/py.typed`** — empty file, signals PEP 561 support.

### 3.2 [High] Move `verification_script.py` to `scripts/`

Aletheca has a clean `scripts/verify.py`. Aireloom has `verification_script.py` at the repo root, cluttering the top level.

**Move to `scripts/verification_script.py`** and update any references.

### 3.3 [Medium] Add `.python-version` File

Aletheca has `.python-version` pinning the Python version. Aireloom doesn't.

**Add `.python-version`** with `3.12` (or whatever the target is).

### 3.4 [Medium] Clean Up Committed `.ruff_cache/`

Aireloom has `.ruff_cache/` committed (visible in directory listing). Should be in `.gitignore`.

**Add `.ruff_cache/` to `.gitignore`** and `git rm -r --cached .ruff_cache/`.

### 3.5 [Low] Consider Typed ID Models

Aletheca has dedicated `src/aletheca/models/ids.py` with typed ID models per entity (WorkIds, AuthorIds, SourceIds, etc.). Aireloom uses `list[str]` or `dict` for PIDs and identifiers.

**Consider** adding typed PID/ID models for better autocomplete and validation, especially for the complex `Pid` structure in research products.

---

## 4. Potential Bibliofabric Improvements

> These are cross-cutting improvements that could benefit both libraries. Flag for discussion, not immediate implementation.

### 4.1 Generalize Filter Serialization

Aletheca's `AlethecaResourceClient._serialize_filters()` overrides the base to produce OpenAlex's `filter=key:value,key:value` format. This is a clean pattern that could be generalized:

- Add a `_filter_serializer` protocol or class attribute to `BaseResourceClient`
- Default: individual query params (current behavior)
- Override: single `filter` param with custom joining (OpenAlex pattern)
- Override: `extra="forbid"` vs `extra="allow"` config per-API

**Impact:** Reduces boilerplate in aletheca's `_standard.py` from 67 lines to ~10 lines of config.

### 4.2 Document Iterator Helpers in Base Framework

`collect()`, `count()`, `first()` come from bibliofabric mixins but aren't documented in the framework itself. Each consumer (aireloom, aletheca) documents them independently.

**Add a `docs/` or README section in bibliofabric** documenting the mixin-provided methods so consumers can link to it.

### 4.3 Shared `SafeTypes` Module

Both libraries implement `SafeList` and `SafeStr` validators independently. The logic is identical.

**Move to `bibliofabric.safe_types`** as a shared module, import in both libraries.

---

## 5. Design Differences (Intentional, Not Gaps)

| Aspect | Aireloom | Aletheca | Reason |
|--------|----------|----------|--------|
| Filter `extra` | `"forbid"` | `"allow"` | OpenAlex has many undocumented filters; OpenAIRE is stricter |
| Auth | OAuth2 + Bearer | API key query param | Different API auth schemes |
| API versioning | v1/v2/v3 routing | Single version | OpenAlex has one version |
| Unwrapper | Complex (header + results) | Simple (meta + results) | Different response envelopes |
| `_helpers.py` | PID extraction | DOI/ID normalization | Different identifier ecosystems |
| `analysis` extras | More deps (seaborn, plotly, networkx) | Fewer deps | Intentionally leaner for aletheca |
| Custom resource clients | ScholixClient (0-indexed pagination, different base URL) | All standard mixin-based | OpenAlex has uniform endpoints |
| Computed model properties | Yes (doi, is_open_access, etc.) | No | OpenAlex returns flatter structures |

---

## 6. Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| P0 | Expand examples (2.1) | Medium |
| P0 | Add ergonomics docs (2.2) | Small |
| P1 | Add changelog doc (2.3) | Small |
| P1 | Expand public API exports (2.6) | Small |
| P1 | Add auth tests (2.5) | Small |
| P2 | Add live API tests (2.4) | Small |
| P2 | Add marimo iframes in docs (2.7) | Small |
| P3 | Computed properties (2.8) | Deferred |

**Total estimated new files:** ~10 examples + 2 docs pages + 2 test files
**Total estimated new lines:** ~1,500-2,000
