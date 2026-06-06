# Works

The Works endpoint is the core of the OpenAlex API. A Work represents any scholarly output — journal articles, books, datasets, theses, conference papers, and more. Each work links to authors, institutions, sources, topics, and other entities.

## Quick Start

### Get a work by OpenAlex ID

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")
    print(work.title)
    print(work.publication_year)
    print(work.doi)
```

### Get a work by DOI

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("https://doi.org/10.1038/nature12373")
    print(work.id)  # OpenAlex ID (e.g. W2741809807)
    print(work.cited_by_count)
```

The `get` method accepts OpenAlex IDs (`W1234567890`), full URLs, or DOIs (with or without the `https://doi.org/` prefix).

### Search for works

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
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
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
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
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    # By OpenAlex author ID
    filters = WorksFilters(authorships_author_id="A5023888391")
    results = await session.works.search(filters=filters, page_size=25)

    # Multiple authors (pipe-separated)
    filters = WorksFilters(authorships_author_id="A5023888391|A5084217198")
```

### Filter by institution

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    filters = WorksFilters(
        authorships_institutions_id="I31371856",  # Stanford University
        publication_year_range="2020-2024",
    )
    results = await session.works.search(filters=filters, page_size=50)
```

### Filter by year and date

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    # Exact year
    filters = WorksFilters(publication_year=2024)

    # Year range
    filters = WorksFilters(publication_year_range="2020-2024")

    # Date range (YYYY-MM-DD)
    filters = WorksFilters(
        from_publication_date="2023-01-01",
        to_publication_date="2023-12-31",
    )
```

### Filter by source (journal/conference)

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    # Works published in a specific journal
    filters = WorksFilters(
        primary_location_source_id="S137030756",  # Nature
    )

    # Works from any source type
    filters = WorksFilters(primary_location_source_type="journal")
```

### Presence and boolean filters

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    filters = WorksFilters(
        has_abstract=True,
        has_doi=True,
        is_oa=True,
        type="article",
    )
```

## Iteration (Cursor Pagination)

For large result sets, use `iterate` to automatically handle cursor-based pagination:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    filters = WorksFilters(
        authorships_author_id="A5023888391",
        publication_year_range="2020-2024",
    )
    async for work in session.works.iterate(
        filters=filters,
        per_page=200,  # max allowed by OpenAlex
        sort="cited_by_count:desc",
    ):
        print(f"{work.title} — cited {work.cited_by_count} times")
```

Sorting uses the format `field:direction` (e.g. `"publication_date:desc"`, `"cited_by_count:asc"`).

## Citing and Referenced Works

### Get works that cite a given work

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")

    # Using the convenience query
    citing = await session.queries.citing_works(work.id, limit=100)
    print(f"Found {len(citing)} citing works")
```

### Get works referenced by a given work

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
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
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    # Works that cite a specific work
    filters = WorksFilters(cites="W2741809807")

    # Works cited by a specific work
    filters = WorksFilters(cited_by="W2741809807")
```

## Abstract Reconstruction

OpenAlex stores abstracts as an inverted index to comply with publisher agreements. Use `reconstruct_abstract` to convert it back to plain text:

```python
from syntheca import SynthecaSession
from syntheca._helpers import reconstruct_abstract

async with SynthecaSession() as session:
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
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    works = await session.queries.works_by_doi([
        "10.1038/nature12373",
        "10.1126/science.1248506",
    ])
    for work in works:
        print(f"{work.doi}: {work.title}")
```

### Fetch works by author name

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    works = await session.queries.works_by_author("John Smith", limit=50)
    for work in works:
        print(f"{work.publication_year}: {work.title}")
```

### Fetch works by institution name

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
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
| `is_oa` | `bool \| None` | Whether the work is open access |
| `cited_by_count` | `int` | Number of citations |
| `authorships` | `list[Authorship]` | Author and affiliation data |
| `locations` | `list[Location]` | Places the work can be found |
| `primary_location` | `Location \| None` | Best available location |
| `referenced_works` | `list[str]` | OpenAlex IDs of cited works |
| `topics` | `list[DehydratedTopic]` | Associated topics |
| `keywords` | `list[DehydratedKeyword]` | Associated keywords |
| `grants` | `list[Grant]` | Grant/funding information |
| `abstract_inverted_index` | `dict \| None` | Inverted index for abstract reconstruction |

## Notes

- OpenAlex IDs for works start with `W` (e.g. `W2741809807`).
- The maximum `per_page` value is 200. Use cursor pagination (`iterate`) for large result sets.
- Abstracts are stored as inverted indexes; use `reconstruct_abstract()` to get plain text.
- DOIs can be passed with or without the `https://doi.org/` prefix.
- Multiple values in filters can be pipe-separated (e.g. `"A123|A456"`).
- Set the `SYNTHECA_OPENALEX_API_KEY` environment variable or pass `api_key` to `SynthecaSession` for faster access via the polite pool.
