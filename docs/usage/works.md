# Works

The Works endpoint is the core of the OpenAlex API. A Work represents any scholarly output — journal articles, books, datasets, theses, conference papers, and more. Each work links to authors, institutions, sources, topics, and other entities.

## Quick Start

### Get a work by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")
    print(work.title)
    print(work.publication_year)
    print(work.doi)
```

### Get a work by DOI

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("https://doi.org/10.1038/nature12373")
    print(work.id)  # OpenAlex ID (e.g. W2741809807)
    print(work.cited_by_count)
```

The `get` method accepts OpenAlex IDs (`W1234567890`), full URLs, or DOIs (with or without the `https://doi.org/` prefix).

### Search for works

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.works.search(
        search="climate change adaptation",
        page_size=25,
    )
    for work in results.results:
        print(f"{work.title} ({work.publication_year})")
```

## Filtering

Use `WorksFilters` to construct structured filter queries. Nested OpenAlex filter fields (e.g. `authorships.author.id`) are mapped to Python-safe attribute names using Pydantic aliases.

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(
        publication_year=2024,
        is_oa=True,
        language="en",
    )
    results = await session.works.search(
        search="machine learning",
        filters=filters,
        page_size=50,
    )
```

### Filter by author

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    # By OpenAlex author ID
    filters = WorksFilters(authorships_author_id="A5023888391")
    results = await session.works.search(filters=filters, page_size=25)

    # Multiple authors (pipe-separated)
    filters = WorksFilters(authorships_author_id="A5023888391|A5084217198")
```

### Filter by institution

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(
        authorships_institutions_id="I31371856",  # Stanford University
        from_publication_date="2020-01-01",
    )
    results = await session.works.search(filters=filters, page_size=50)
```

### Filter by year and date

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    # Exact year
    filters = WorksFilters(publication_year=2024)

    # Year range
    filters = WorksFilters(publication_year=2024)  # Use from_publication_date/to_publication_date for ranges

    # Date range (YYYY-MM-DD)
    filters = WorksFilters(
        from_publication_date="2023-01-01",
        to_publication_date="2023-12-31",
    )
```

### Filter by source (journal/conference)

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    # Works published in a specific journal
    filters = WorksFilters(
        primary_location_source_id="S137030756",  # Nature
    )

    # Works from any source type
    filters = WorksFilters(primary_location_source_type="journal")
```

### Presence and boolean filters

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(
        has_abstract=True,
        has_doi=True,
        is_oa=True,
        type="article",
    )
```

### Filter by topic

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(topics_id="T10100")
    async for work in session.works.iterate(filters=filters, page_size=100):
        print(work.display_name)
```

## Iteration (Cursor Pagination)

For large result sets, use `iterate` to automatically handle cursor-based pagination:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(
        authorships_author_id="A5023888391",
        from_publication_date="2020-01-01",
    )
    async for work in session.works.iterate(
        filters=filters,
        page_size=100,  # max allowed by OpenAlex
        sort_by="cited_by_count:desc",
    ):
        print(f"{work.title} — cited {work.cited_by_count} times")
```

Sorting uses the format `field:direction` (e.g. `"publication_date:desc"`, `"cited_by_count:asc"`).

## Citing and Referenced Works

### Get works that cite a given work

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")

    # Using the convenience query
    citing = await session.queries.citing_works(work.id, limit=100)
    print(f"Found {len(citing)} citing works")
```

### Get works referenced by a given work

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")

    # Using the convenience query
    refs = await session.queries.referenced_works(work.id, limit=50)
    for ref in refs:
        print(ref.title)

    # Or access the raw reference IDs directly
    for ref_id in work.referenced_works:
        print(ref_id)
```

### Using filters directly

```python
from aletheca import AlethecaSession
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    # Works that cite a specific work
    filters = WorksFilters(cites="W2741809807")

    # Works cited by a specific work
    filters = WorksFilters(cited_by="W2741809807")
```

## Abstract Reconstruction

OpenAlex stores abstracts as an inverted index to comply with publisher agreements. Use `reconstruct_abstract` to convert it back to plain text:

```python
from aletheca import AlethecaSession
# Note: _helpers is a private module; it may be relocated in a future release.
from aletheca._helpers import reconstruct_abstract

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")

    if work.abstract_inverted_index:
        abstract = reconstruct_abstract(work.abstract_inverted_index)
        print(abstract)
    else:
        print("No abstract available")
```

## Convenience Queries

The `session.queries` accessor provides higher-level helpers that compose multiple API calls:

### Fetch works by DOI

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    works = await session.queries.works_by_doi([
        "10.1038/nature12373",
        "10.1126/science.1248506",
    ])
    for work in works:
        print(f"{work.doi}: {work.title}")
```

### Fetch works by author name

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    works = await session.queries.works_by_author("John Smith", limit=50)
    for work in works:
        print(f"{work.publication_year}: {work.title}")
```

### Fetch works by institution name

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    works = await session.queries.works_by_institution("Stanford University", limit=100)
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str \| None` | Work title |
| `publication_year` | `int \| None` | Year of publication |
| `publication_date` | `str \| None` | Full date (YYYY-MM-DD) |
| `doi` | `str \| None` | DOI identifier |
| `type` | `str \| None` | Work type (article, book, dataset, etc.) |
| `open_access.is_oa` | `bool \| None` | Whether the work is open access (nested in `open_access`) |
| `cited_by_count` | `int` | Number of citations |
| `authorships` | `list[Authorship]` | Author and affiliation data |
| `locations` | `list[Location]` | Places the work can be found |
| `primary_location` | `Location \| None` | Best available location |
| `parent_works` | `list[RelatedWork]` | Works this work is part of, each with its `relationship` (`volume`, `component`, `data-series`, `part`) |
| `lineage` | `list[str]` | The work's own OpenAlex ID first, then every ancestor's, nearest first |
| `child_works_count` | `int \| None` | How many works name this work as a parent |
| `is_traditional` | `bool \| None` | True for traditional scholarly types (articles, books, chapters, conference papers) |
| `referenced_works` | `list[str]` | OpenAlex IDs of cited works |
| `topics` | `list[DehydratedTopic]` | Associated topics |
| `keywords` | `list[DehydratedKeyword]` | Associated keywords |
| `content_urls` | `ContentUrls \| None` | Content URLs as a dict with `pdf` and `grobid_xml` keys (not `content_url` as in the spec) |
| `abstract_inverted_index` | `dict \| None` | Inverted index for abstract reconstruction |

## Parent and child works

A work can be part of another work: a chapter in a book, a figure in a paper,
one record of a data series. The child names the whole in `parent_works`.

```python
async with AlethecaSession() as session:
    work = await session.works.get("W3109397498")
    print(work.child_works_count)  # direct parts, e.g. a book's chapters
    print(work.lineage)            # [own id, parent ids nearest first]
```

Pieces that are not scholarly works on their own (figures, front matter,
single data records) are left out of list results by default. Pass
`include_parts=True` to bring them back:

```python
from aletheca.endpoints import WorksFilters

async with AlethecaSession() as session:
    filters = WorksFilters(parent_works_id="W3109397498", include_parts=True)
    async for part in session.works.iterate(filters=filters):
        print(part.display_name)
```

The pieces of expansion works (most Zenodo records) additionally need
`corpus="all"` in the filters.

## Filter reference

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

### Part-of (Parent/Child) Filters

A work can be part of another work: a chapter in a book, a figure in a paper.
Filtering on any of these also shows pieces that the default view leaves out.

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `has_parent_work` | `has_parent_work` | `bool` | Work is part of another work |
| `parent_works_id` | `parent_works.id` | `str` | Parts of a parent work, e.g. a book's chapters (OpenAlex Work ID) |
| `parent_works_relationship` | `parent_works.relationship` | `str` | Kind of part-of link: `volume`, `component`, `data-series`, `part` |
| `lineage` | `lineage` | `str` | The work and everything under it, at any depth (OpenAlex Work ID) |
| `child_works_count` | `child_works_count` | `str` | Direct child count; supports ranges (e.g. `">100"`) |
| `is_traditional` | `is_traditional` | `bool` | Traditional scholarly types (articles, books, chapters, conference papers) |

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

### Query Parameters

These are standalone query parameters on the works endpoint, not `filter=` keys;
`WorksFilters` serializes them as separate query parameters.

| Field Name | Type | Description |
|-----------|------|-------------|
| `include_parts` | `bool` | Add pieces of other works (figures, front matter, single data records) back to the results; they are left out of the default view |
| `corpus` | `str` | Which corpus to search: `core` (default), `expansion`, or `all` |

## Live API Notes

The OpenAlex OpenAPI spec declares a `content_url` field (singular, type `string`), but the live API returns `content_urls` (plural, type `object` with `pdf` and `grobid_xml` keys). Aletheca follows the live API. Additionally, the spec lists `works_api_url` on Work objects, but the live API does not return this field on works.

## Notes

- OpenAlex IDs for works start with `W` (e.g. `W2741809807`).
- The maximum `per_page` value is 100. Use cursor pagination (`iterate`) for large result sets.
- Abstracts are stored as inverted indexes; use `reconstruct_abstract()` to get plain text.
- DOIs can be passed with or without the `https://doi.org/` prefix.
- Multiple values in filters can be pipe-separated (e.g. `"A123|A456"`).
- Set the `ALETHECA_API_KEY` environment variable or pass `api_key` to `AlethecaClient` for the $1/day budget and full cursor paging.
