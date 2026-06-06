# Works Endpoint

The Works endpoint is the primary endpoint in OpenAlex, providing access to scholarly works
(papers, articles, books, datasets, etc.).

**Endpoint path:** `works`
**Client access:** `session.works`

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    # Iterate all works matching a filter
    async for work in session.works.iterate(
        filters=WorksFilters(publication_year=2024, is_oa=True),
        per_page=200,
    ):
        print(work.display_name)
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.works.get("W123")` | Fetch a single work by OpenAlex ID or DOI |
| Search | `session.works.search("machine learning")` | Full-text search across works |
| Iterate | `session.works.iterate(filters=...)` | Cursor-based pagination over filtered results |

## WorksFilters Field Reference

All filter fields accept pipe-delimited values for OR logic (e.g., `type:article|book-review`).
Range filters accept a format like `2020-2024`.

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `publication_year` | `publication_year` | `int` | Exact publication year (e.g., `2024`) |
| `publication_date` | `publication_date` | `str` | Exact date (ISO format, e.g., `"2024-01-15"`) |
| `from_publication_date` | `from_publication_date` | `str` | Lower bound date (inclusive) |
| `to_publication_date` | `to_publication_date` | `str` | Upper bound date (inclusive) |
| `type` | `type` | `str` | Work type: `article`, `book`, `book-chapter`, `dataset`, `dissertation`, `editorial`, `erratum`, `letter`, `other`, `paratext`, `peer-review`, `reference-entry`, `report`, `review`, `standard` |
| `is_oa` | `is_oa` | `bool` | Whether the work is Open Access |
| `doi` | `doi` | `str` | DOI identifier (e.g., `"10.1234/abc"`) |
| `pmid` | `pmid` | `str` | PubMed ID |
| `language` | `language` | `str` | ISO 639-1 language code (e.g., `"en"`, `"zh"`) |

### Citation & Relationship Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `cites` | `cites` | `str` | OpenAlex ID(s) of works this work cites. Pipe-delimited for multiple. |
| `cited_by` | `cited_by` | `str` | OpenAlex ID(s) of works that cite this work |
| `related_to` | `related_to` | `str` | OpenAlex ID of a work to find related works for |

### Authorship & Institution Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `authorships_author_id` | `authorships.author.id` | `str` | OpenAlex Author ID. Pipe-delimited for multiple (OR). |
| `authorships_institutions_id` | `authorships.institutions.id` | `str` | OpenAlex Institution ID for author affiliations |

### Topic & Concept Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `concepts_id` | `concepts.id` | `str` | Concept ID (deprecated; prefer `topics_id`) |
| `topics_id` | `topics.id` | `str` | OpenAlex Topic ID. Pipe-delimited for multiple. |

### Source (Journal/Repository) Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `primary_location_source_id` | `primary_location.source.id` | `str` | Source ID of the primary location |
| `primary_location_source_type` | `primary_location.source.type` | `str` | Source type: `journal`, `repository`, `conference`, `ebook platform`, `book series` |
| `primary_location_source_has_issn` | `primary_location.source.has_issn` | `bool` | Whether the primary source has an ISSN |
| `primary_location_is_oa` | `primary_location.is_oa` | `bool` | Whether the primary location is OA |
| `locations_is_oa` | `locations.is_oa` | `bool` | Whether any location is OA |
| `locations_source_id` | `locations.source.id` | `str` | Source ID for any location |
| `locations_source_type` | `locations.source.type` | `str` | Source type for any location |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `title_search` | `title.search` | `str` | Search within work titles |
| `abstract_search` | `abstract.search` | `str` | Search within abstracts |
| `default_search` | `default.search` | `str` | Search across title + abstract + display_name |
| `fulltext_search` | `fulltext.search` | `str` | Full-text search (requires fulltext index) |
| `display_name_search` | `display_name.search` | `str` | Search within display name |
| `title_and_abstract_search` | `title_and_abstract.search` | `str` | Search across title and abstract combined |
| `raw_affiliation_strings_search` | `raw_affiliation_strings.search` | `str` | Search within raw affiliation strings |

### Boolean Presence Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `has_doi` | `has_doi` | `bool` | Work has a DOI |
| `has_pmid` | `has_pmid` | `bool` | Work has a PubMed ID |
| `has_pmcid` | `has_pmcid` | `bool` | Work has a PubMed Central ID |
| `has_orcid` | `has_orcid` | `bool` | At least one author has an ORCID |
| `has_abstract` | `has_abstract` | `bool` | Work has an abstract |
| `has_fulltext` | `has_fulltext` | `bool` | Full text is available |
| `has_references` | `has_references` | `bool` | Work has reference list |
| `has_oa_accepted_or_published_version` | `has_oa_accepted_or_published_version` | `bool` | Has an OA accepted/published version |
| `has_oa_submitted_version` | `has_oa_submitted_version` | `bool` | Has an OA submitted (preprint) version |

### Administrative Date Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `from_created_date` | `from_created_date` | `str` | Created in OpenAlex on or after this date |
| `to_created_date` | `to_created_date` | `str` | Created in OpenAlex on or before this date |
| `from_updated_date` | `from_updated_date` | `str` | Updated in OpenAlex on or after this date |
| `to_updated_date` | `to_updated_date` | `str` | Updated in OpenAlex on or before this date |

### Count & Version Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `authors_count` | `authors_count` | `int` | Number of authors |
| `best_oa_version` | `best_oa_version` | `str` | Best OA version type |
| `version` | `version` | `str` | Work version |

## Usage Examples

### Filter by author and year

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(
        authorships_author_id="A5023888391",
        publication_year=2024,
        type="article",
    )
    async for work in session.works.iterate(filters=filters):
        print(f"{work.display_name} — {work.publication_year}")
```

### Search works by topic

```python
async with AlethecaSession() as session:
    filters = WorksFilters(topics_id="T10100")
    async for work in session.works.iterate(filters=filters, per_page=200):
        print(work.display_name)
```

### Get works citing a specific paper

```python
async with AlethecaSession() as session:
    filters = WorksFilters(cited_by="W2741809807")
    results = await session.works.search(filters=filters)
    for work in results.results:
        print(work.display_name)
```

### Combined filters with presence checks

```python
async with AlethecaSession() as session:
    filters = WorksFilters(
        publication_year=2024,
        has_doi=True,
        has_abstract=True,
        is_oa=True,
        language="en",
    )
    async for work in session.works.iterate(filters=filters):
        print(work.doi)
```
