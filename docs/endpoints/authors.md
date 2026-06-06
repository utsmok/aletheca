# Authors Endpoint

The Authors endpoint provides access to author records in OpenAlex, including
researchers' affiliations, citation metrics, and ORCID identifiers.

**Endpoint path:** `authors`
**Client access:** `session.authors`

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    async for author in session.authors.iterate(
        filters=AuthorsFilters(has_orcid=True),
    ):
        print(f"{author.display_name} — {author.orcid}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.authors.get("A123")` | Fetch a single author by OpenAlex ID |
| Search | `session.authors.search("Einstein")` | Search authors by name |
| Iterate | `session.authors.iterate(filters=...)` | Cursor-based pagination over filtered results |

## AuthorsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `orcid` | `orcid` | `str` | ORCID iD (e.g., `"0000-0001-2345-6789"`) |
| `display_name` | `display_name` | `str` | Exact display name match |
| `works_count` | `works_count` | `int` | Exact number of works |
| `cited_by_count` | `cited_by_count` | `int` | Exact citation count |

### Affiliation Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `affiliation_institution_id` | `affiliations.institution.id` | `str` | Current affiliation institution ID |
| `last_known_institutions_id` | `last_known_institutions.id` | `str` | Last known institution ID |
| `affiliations_institution_country_code` | `affiliations.institution.country_code` | `str` | Affiliated institution country (ISO 3166-1 alpha-2) |
| `affiliations_institution_lineage` | `affiliations.institution.lineage` | `str` | Institution lineage (parent chain) |
| `affiliations_institution_ror` | `affiliations.institution.ror` | `str` | ROR ID of affiliated institution |
| `affiliations_institution_type` | `affiliations.institution.type` | `str` | Type of affiliated institution (`education`, `facility`, `healthcare`, `company`, `archive`, `nonprofit`, `government`, `facility`, `other`) |
| `last_known_institutions_country_code` | `last_known_institutions.country_code` | `str` | Last known institution country code |
| `last_known_institutions_lineage` | `last_known_institutions.lineage` | `str` | Last known institution lineage |
| `last_known_institutions_ror` | `last_known_institutions.ror` | `str` | Last known institution ROR ID |
| `last_known_institutions_type` | `last_known_institutions.type` | `str` | Last known institution type |
| `last_known_institution_continent` | `last_known_institution.continent` | `str` | Continent of last known institution |
| `last_known_institution_is_global_south` | `last_known_institution.is_global_south` | `bool` | Whether last known institution is in the Global South |

### Topic & Concept Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `topics_id` | `topics.id` | `str` | OpenAlex Topic ID associated with the author's work |
| `x_concepts_id` | `x_concepts.id` | `str` | Concept ID (deprecated; prefer `topics_id`) |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

### Boolean & Presence Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `has_orcid` | `has_orcid` | `bool` | Whether the author has an ORCID iD |
| `scopus` | `scopus` | `int` | Scopus author ID |

### ID & Summary Stats Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `ids_openalex` | `ids.openalex` | `str` | OpenAlex ID from the ids object |
| `summary_stats_2yr_mean_citedness` | `summary_stats.2yr_mean_citedness` | `float` | 2-year mean citedness |
| `summary_stats_h_index` | `summary_stats.h_index` | `int` | h-index |
| `summary_stats_i10_index` | `summary_stats.i10_index` | `int` | i10-index |

## Usage Examples

### Find authors at a specific institution

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(
        affiliations_institution_id="I136199904",
        has_orcid=True,
    )
    async for author in session.authors.iterate(filters=filters):
        print(f"{author.display_name} — h-index: {author.summary_stats.h_index if author.summary_stats else 'N/A'}")
```

### Search authors by name

```python
async with SynthecaSession() as session:
    filters = AuthorsFilters(display_name_search="Albert Einstein")
    async for author in session.authors.iterate(filters=filters):
        print(author.display_name)
```

### Filter by country and topic

```python
async with SynthecaSession() as session:
    filters = AuthorsFilters(
        affiliations_institution_country_code="DE",
        topics_id="T10100",
    )
    async for author in session.authors.iterate(filters=filters):
        print(author.display_name)
```
