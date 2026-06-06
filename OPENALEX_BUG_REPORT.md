# OpenAlex API Bug Report

**Date:** 2026-06-05
**Reporter:** Syntheca client library maintainers
**APIs tested:** OpenAlex REST API (`api.openalex.org`), all 9 entity endpoints
**Method:** Every finding below was verified by: (1) fetching live API responses, (2) reading the OpenAPI spec at `developers.openalex.org/api-reference/openapi.json`, and (3) reading the documentation pages at `developers.openalex.org`. Discrepancies are reported only where at least two of these three sources disagree.

---

## How to Reproduce

Each bug includes a `curl`-able URL. All work without an API key. Where relevant, the corresponding doc page and OpenAPI spec location are linked.

---

## 1. OpenAPI Spec vs Live API — Missing Fields

The OpenAPI spec is substantially incomplete for most entity types. Fields returned by the live API are missing from the spec schemas. Below is a per-entity accounting.

### SPEC-W1: Work — 12 live fields missing from spec, 1 field in spec but not in live API

**OpenAPI spec:** `Work` schema in [`openapi.json`](https://developers.openalex.org/api-reference/openapi.json) — has 38 properties
**Live API:** Returns 49 fields per work object

**Fields in spec but NOT returned by live API:**
- `content_url` (string, nullable) — the live API returns `content_urls` instead (see SPEC-W2 below)

**Fields returned by live API but NOT in spec:**

| Field | Live Type | Example Value |
|-------|-----------|---------------|
| `apc_list` | object \| null | `null` |
| `apc_paid` | object \| null | `null` |
| `concepts` | array | `[{"id": "...", "wikidata": "...", "display_name": "...", ...}]` |
| `content_urls` | object \| null | `{"pdf": "https://...", "grobid_xml": "https://..."}` |
| `corresponding_author_ids` | array | `["https://openalex.org/A5039600762"]` |
| `corresponding_institution_ids` | array | `["https://openalex.org/I199525922"]` |
| `countries_distinct_count` | integer | `1` |
| `has_fulltext` | boolean | `true` |
| `institutions` | array | `[]` |
| `institutions_distinct_count` | integer | `2` |
| `is_xpac` | boolean | `false` |
| `locations_count` | integer | `3` |

**Reproduce:**
```
GET https://api.openalex.org/works?per_page=1
→ Compare response keys against the Work schema in the OpenAPI spec
```

---

### SPEC-W2: `content_url` in spec → `content_urls` in live — wrong name AND wrong type

**OpenAPI spec:** Declares `content_url` (singular, type: `string`, nullable)
**Live API:** Returns `content_urls` (plural, type: **object** with keys `pdf`, `grobid_xml`, or `null`)

Two independent errors in one field: wrong name (singular vs plural) and wrong type (string vs object). ~24% of works have non-null values.

**Reproduce:**
```
GET https://api.openalex.org/works/W3038568908
→ "content_urls": {"pdf": "https://content.openalex.org/works/W3038568908.pdf", "grobid_xml": "https://content.openalex.org/works/W3038568908.grobid-xml"}
```

---

### SPEC-A1: Author — 2 fields in spec not returned by live API, 5 live fields missing from spec

**Fields in spec but NOT returned by live API:**
- `longest_name` (string)
- `parsed_longest_name` (object with `first`, `last`, `middle`)

**Fields returned by live API but NOT in spec:**

| Field | Live Type | Notes |
|-------|-----------|-------|
| `block_key` | string | Internal deduplication key |
| `full_name` | string | Full formatted name |
| `raw_author_names` | array | Raw name variants |
| `topic_share` | array | Topic relevance scores |
| `x_concepts` | array | Deprecated concepts, still returned |

**Reproduce:**
```
GET https://api.openalex.org/authors?per_page=1
→ Response includes block_key, full_name, raw_author_names, topic_share, x_concepts
→ Response does NOT include longest_name, parsed_longest_name
```

---

### SPEC-S1: Source — 16 live fields missing from spec

The Source schema in the spec has only 20 properties. The live API returns 36 fields.
**Fields returned by live API but NOT in spec:**

| Field | Live Type | Notes |
|-------|-----------|-------|
| `alternate_titles` | array | Alternate names |
| `apc_prices` | array \| null | Detailed APC pricing |
| `country_code` | string \| null | ISO country code |
| `first_publication_year` | integer \| null | First publication |
| `is_core` | boolean | CORE index status |
| `is_high_oa_rate` | boolean | High OA rate flag |
| `is_high_oa_rate_since_year` | integer \| null | Since when |
| `is_in_doaj_since_year` | integer \| null | DOAJ since |
| `is_in_scielo` | boolean | SciELO status |
| `is_ojs` | boolean | OJS platform flag |
| `last_publication_year` | integer \| null | Last publication |
| `oa_flip_year` | integer \| null | OA flip year |
| `oa_works_count` | integer | OA work count |
| `societies` | array | Related societies |
| `topic_share` | array | Topic shares |
| `topics` | array | Topics |

**Note:** Many of these fields (e.g., `is_ojs`, `oa_flip_year`, `is_high_oa_rate`) appear in the Source filter table on the docs page, confirming they are intentionally part of the API surface. They're just missing from the OpenAPI spec.

**Reproduce:**
```
GET https://api.openalex.org/sources?per_page=1
→ Response has 37 fields; spec only covers 21
```

**Doc page:** https://developers.openalex.org/api-reference/sources — filter table lists many of these fields

---

### SPEC-I1: Institution — 9 live fields missing from spec

**Fields returned by live API but NOT in spec:**

| Field | Live Type | Notes |
|-------|-----------|-------|
| `associated_institutions` | array | Related institutions with roles |
| `international` | object | International collaboration metrics |
| `is_super_system` | boolean | Super-system flag |
| `repositories` | array | Associated repositories |
| `roles` | array | Cross-entity roles (e.g., funder role) |
| `status` | string | e.g., "active" |
| `topic_share` | array | Topic shares |
| `topics` | array | Topics |
| `type_id` | string | Institution type OpenAlex ID |

**Reproduce:**
```
GET https://api.openalex.org/institutions?per_page=1
→ Compare response keys against Institution schema in spec
```

---

### SPEC-T1: Topic — `siblings` field missing from spec

**OpenAPI spec:** `Topic` schema has 12 properties, no `siblings` field.
**Live API:** Returns `siblings` as an array of `{id, display_name}` objects.

**Reproduce:**
```
GET https://api.openalex.org/topics/T10100
→ "siblings": [{"id": "https://openalex.org/T10020", "display_name": "Quantum Information and Cryptography"}, ...]
```
(76 siblings for this topic)

---

### SPEC-P1: Publisher — 5 live fields missing from spec

**Fields returned by live API but NOT in spec:**

| Field | Live Type | Notes |
|-------|-----------|-------|
| `homepage_url` | string | Publisher homepage |
| `image_thumbnail_url` | string | Thumbnail image |
| `image_url` | string | Full image |
| `roles` | array | Cross-entity roles |
| `summary_stats` | object | Citation metrics |

**Reproduce:**
```
GET https://api.openalex.org/publishers?per_page=1
→ Response includes homepage_url, image_url, roles, summary_stats etc.
```

---

### SPEC-F1: Funder — `grants_count` in spec, `awards_count` in live; `works_api_url` in spec but not in live

Three issues:

1. **`grants_count` → `awards_count` rename not reflected.** The spec has `grants_count` (integer). The live API returns `awards_count` instead. The `grants` → `awards` transition was documented as deprecated in the `llms.txt` file, but the spec schema was never updated.

2. **`works_api_url` in spec but not in live API.** The Funder schema includes `works_api_url` (string), but the live API does not return this field on funder objects. All other entities that have `works_api_url` in the spec (Author, Source, Institution, Topic, Keyword) correctly return it.

3. **3 live fields missing from spec:** `awards_count`, `roles`, `summary_stats`.

**Reproduce:**
```
GET https://api.openalex.org/funders/F4320306100
→ "awards_count": 70707, "roles": [...], "summary_stats": {...}
→ NO "grants_count", NO "works_api_url"
```

---

### SPEC-AW1: Award — 3 live fields missing from AwardFull spec

**Fields returned by live API but NOT in `AwardFull` spec schema:**

| Field | Live Type | Notes |
|-------|-----------|-------|
| `institution_awarded` | array | Always a list (even when empty `[]`) |
| `primary_topic` | object \| null | Topic object |
| `topics` | array \| null | Topics list |

**Reproduce:**
```
GET https://api.openalex.org/awards?per_page=1
→ Response includes institution_awarded, primary_topic, topics
```

---

## 2. Documentation Errors

### DOC-1: `per_page` maximum documented as 100 in `llms.txt`, but 200 works

**Location:** https://developers.openalex.org/llms.txt
**Documented:** `per_page max: 100`
**Actual:** `per_page=200` returns 200 results without error

**Reproduce:**
```
GET https://api.openalex.org/works?per_page=200
→ 200 {"meta": {"per_page": 200, ...}}, 200 results returned
```

---

### DOC-2: Awards endpoint not listed in `llms.txt`

**Location:** https://developers.openalex.org/llms.txt
**Listed endpoints:** `/works`, `/authors`, `/sources`, `/institutions`, `/topics`, `/keywords`, `/publishers`, `/funders`
**Missing:** `GET /awards`

The awards endpoint exists (14.7M records), has OpenAPI spec coverage, has dedicated docs pages, but is absent from the `llms.txt` quick reference.

**Reproduce:**
```
GET https://api.openalex.org/awards?per_page=1
→ 200 {"meta": {"count": 14748865, ...}, "results": [...]}
```

---

### DOC-3: Award `institution_awarded` not documented anywhere

**Location:** Award docs pages at `developers.openalex.org/api-reference/awards/*`

The `institution_awarded` field is:
- Returned by the live API on every award object
- Missing from the `AwardFull` OpenAPI schema
- Not mentioned on the "Get a single award" docs page (other fields like `lead_investigator`, `funded_outputs`, `provenance` are documented)
- Not in the award filter table on the main awards page

This field is completely invisible to anyone relying solely on docs or spec.

**Reproduce:**
```
GET https://api.openalex.org/awards?per_page=1
→ "institution_awarded": [] (always present, type: array)
```

---

### DOC-4: Awards have undocumented filters — 15+ nested filter paths not in docs

**Location:** https://developers.openalex.org/api-reference/awards — filter table

The docs filter table lists ~23 filters. By sending an invalid filter to the API and reading the error message, we discovered at least 38 valid filter fields. The 15+ undocumented ones include:

- `institution_awarded.continent`, `.country_code`, `.id`, `.lineage`, `.ror`, `.type`
- `lead_investigator.affiliation.country`, `.affiliation.name`, `.family_name`, `.given_name`, `.orcid`
- `primary_topic.domain.id`, `.field.id`, `.id`, `.subfield.id`
- `topics.domain.id`, `.field.id`, `.id`, `.subfield.id`

**Reproduce:**
```
GET https://api.openalex.org/awards?filter=nonexistent_field:foo&per_page=1
→ 400 with message listing all 38+ valid filter fields
```

---

## 3. Live API Behaviors Worth Documenting

### API-1: `institution_awarded` is a list despite singular name

**Endpoint:** `GET /awards/{id}`

The field `institution_awarded` always returns an array (sometimes empty `[]`). The singular name suggests a single object, which may mislead consumers. Each element has shape `{id, display_name, ror, country_code, type, lineage}`.

**Reproduce:**
```
GET https://api.openalex.org/awards?per_page=5
→ Every result: "institution_awarded": [] (always array, never null or single object)
```

---

### API-2: `funded_outputs` on Awards returns raw ID strings, not objects

**Endpoint:** `GET /awards/{id}`

The `funded_outputs` field returns `list[str]` of OpenAlex work URLs (e.g., `"https://openalex.org/W34046"`). Other relationships on the same entity return structured objects (`funder` returns `{id, display_name, doi}`, `primary_topic` returns a full topic object). The inconsistency makes the API harder to consume.

The spec correctly types this as `{"type": "array", "items": {"type": "string"}}` — so the spec is accurate, but the design is inconsistent with other relationships.

**Reproduce:**
```
GET https://api.openalex.org/awards?per_page=1
→ "funded_outputs": ["https://openalex.org/W34046", "https://openalex.org/W72973", ...]
```

---

### API-3: Source `fatcat` ID no longer returned

**Endpoint:** `GET /sources/{id}`

The `ids` object on Source entities no longer includes a `fatcat` field. All tested sources return `ids: {openalex, issn_l, issn, mag, wikidata}` — no `fatcat`. If this field was intentionally removed, it should be documented as a breaking change.

**Reproduce:**
```
GET https://api.openalex.org/sources?per_page=10
→ Every result's ids: {openalex, issn_l, issn, mag, wikidata} — no fatcat
```

---

## 4. Broader Suggestions

### SUGGEST-1: Adopt a formal versioning scheme

The OpenAlex API has no stated version. The OpenAPI spec declares `version: "1.0.0"` but there is no version in the base URL and no changelog. Breaking changes (like `grants_count` → `awards_count`, removal of `fatcat` IDs) happen silently.

**Recommendation:** Add API versioning (e.g., `v1/` prefix or `Accept-Version` header) and maintain a changelog of breaking changes.

---

### SUGGEST-2: Generate the OpenAPI spec from the live API

The OpenAPI spec is substantially incomplete. Across all entity types, the live API returns **50+ fields** that are not modeled in the spec schemas. Additionally, the spec includes at least 3 fields that the live API does not return (`longest_name`, `parsed_longest_name` on Author, `content_url` on Work).

**Recommendation:** Generate the spec from the actual API schema (or at least validate it automatically) to keep it in sync.

---

### SUGGEST-3: Clarify the filter vs entity field relationship

Many filter names don't correspond to entity field names. Examples:
- Entity has `best_oa_location`, filter uses `best_open_version`
- Entity has `open_access.is_oa`, filter uses `is_oa` (top-level shortcut)

**Recommendation:** Add a mapping table showing entity field → filter name for each endpoint.

---

### SUGGEST-4: Document the full list of valid filter values

Filter tables list names and types but don't enumerate accepted values. For example:
- `type` on Works — what are the valid types?
- `oa_status` on Works — what are the valid statuses?
- `funding_type` on Awards — what are the valid types?
- `continent` on Sources — what are the valid continent codes?

**Recommendation:** For enum-like filters, list all accepted values with descriptions.

---

### SUGGEST-5: Provide a structured filter discovery mechanism

Currently the only reliable way to discover all valid filters for an endpoint is to submit an invalid filter and parse the error message. The docs filter tables are incomplete (see DOC-4 for the awards case).

**Recommendation:** Provide a `/filters` metadata endpoint or include the complete filter schema in the OpenAPI spec.

---

## Summary Table

| ID | Severity | Category | Endpoint | Issue |
|----|----------|----------|----------|-------|
| SPEC-W1 | **High** | Spec Incomplete | Works | 12 fields missing from spec, 1 stale field |
| SPEC-W2 | **High** | Spec Error | Works | `content_url` (string) vs `content_urls` (dict) — wrong name AND type |
| SPEC-A1 | Medium | Spec Incomplete | Authors | 2 spec-only fields, 5 live-only fields |
| SPEC-S1 | **High** | Spec Incomplete | Sources | 16 fields missing from spec (incl. filterable ones) |
| SPEC-I1 | Medium | Spec Incomplete | Institutions | 9 fields missing from spec |
| SPEC-T1 | Low | Spec Incomplete | Topics | `siblings` missing from spec |
| SPEC-P1 | Medium | Spec Incomplete | Publishers | 5 fields missing from spec |
| SPEC-F1 | **High** | Spec Error | Funders | `grants_count` stale, `works_api_url` stale, 3 fields missing |
| SPEC-AW1 | Medium | Spec Incomplete | Awards | 3 fields missing from `AwardFull` schema |
| DOC-1 | Medium | Wrong Docs | All | `per_page` max documented as 100, actually 200 |
| DOC-2 | Medium | Missing Docs | Awards | Awards not in `llms.txt` endpoint list |
| DOC-3 | Medium | Missing Docs | Awards | `institution_awarded` not documented anywhere |
| DOC-4 | Medium | Missing Docs | Awards | 15+ nested filters not in docs filter table |
| API-1 | Low | Naming | Awards | `institution_awarded` is a list, name is singular |
| API-2 | Low | Consistency | Awards | `funded_outputs` returns raw strings, not objects |
| API-3 | Low | Removal | Sources | `fatcat` ID no longer returned (undocumented removal) |
