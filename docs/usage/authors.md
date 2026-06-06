# Authors

The Authors endpoint represents individual researchers and scholars. Each author links to their institutional affiliations, publication counts, citation metrics, and works.

## Quick Start

### Get an author by OpenAlex ID

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    author = await session.authors.get("A5023888391")
    print(author.display_name)
    print(author.orcid)
    print(author.works_count)
    print(author.cited_by_count)
```

### Get an author by ORCID

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    author = await session.authors.get("https://orcid.org/0000-0002-1825-0097")
    print(author.display_name)
    print(author.id)
```

The `get` method accepts OpenAlex IDs (`A1234567890`), full URLs, or ORCID identifiers (with or without the `https://orcid.org/` prefix).

### Search for authors

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    results = await session.authors.search(
        search="Andrea Gawrylewski",
        page_size=25,
    )
    for author in results.results:
        print(f"{author.display_name} — {author.works_count} works")
```

## Filtering

Use `AuthorsFilters` to construct structured filter queries:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(
        display_name_search="gawrylewski",
        has_orcid=True,
    )
    results = await session.authors.search(filters=filters, page_size=25)
```

### Filter by institution

Filter authors by their institutional affiliations — either current or historical:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    # Authors affiliated with a specific institution
    filters = AuthorsFilters(
        affiliation_institution_id="I31371856",  # Stanford University
    )
    results = await session.authors.search(filters=filters, page_size=50)

    # Authors at institutions in a specific country
    filters = AuthorsFilters(
        affiliations_institution_country_code="US",
    )

    # Authors at a specific type of institution
    filters = AuthorsFilters(
        affiliations_institution_type="education",
    )

    # Filter by institution lineage (includes parent/child orgs)
    filters = AuthorsFilters(
        affiliations_institution_lineage="I31371856",
    )

    # Filter by ROR ID
    filters = AuthorsFilters(
        affiliations_institution_ror="https://ror.org/00f54p054",
    )
```

### Filter by last known institution

The `last_known_institutions` fields filter on the author's most recent institutional affiliation:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(
        last_known_institutions_id="I31371856",
        last_known_institutions_country_code="US",
    )
    results = await session.authors.search(filters=filters, page_size=25)
```

### Filter by ORCID presence

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(has_orcid=True)
    results = await session.authors.search(filters=filters, page_size=25)
```

### Filter by summary statistics

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(
        summary_stats_h_index=50,
    )
    results = await session.authors.search(filters=filters, page_size=25)
```

## Affiliations

Each author has an `affiliations` list containing their institutional history with year ranges:

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    author = await session.authors.get("A5023888391")

    for aff in author.affiliations:
        institution = aff.institution if hasattr(aff, "institution") else None
        years = aff.years if hasattr(aff, "years") else None
        if institution:
            name = institution.get("display_name") if isinstance(institution, dict) else institution.display_name
            print(f"  {name} ({years})")

    # Current/most recent institutions
    for inst in author.last_known_institutions:
        print(inst.display_name)
```

## Iteration

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AuthorsFilters

async with SynthecaSession() as session:
    filters = AuthorsFilters(
        affiliations_institution_country_code="DE",
    )
    async for author in session.authors.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{author.display_name}: {author.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Author display name |
| `orcid` | `str \| None` | ORCID identifier |
| `works_count` | `int \| None` | Total number of works |
| `cited_by_count` | `int \| None` | Total citations received |
| `affiliations` | `list[DehydratedInstitutionWithYear]` | Institutional affiliations with years |
| `last_known_institutions` | `list[DehydratedInstitution]` | Most recent institutions |
| `counts_by_year` | `list[YearCount]` | Annual works/citations breakdown |
| `summary_stats` | `SummaryStats \| None` | h-index, i10-index, 2yr mean citedness |
| `topics` | `list[TopicCount]` | Topics associated with the author's works |
| `ids` | `AuthorIds \| None` | OpenAlex, ORCID, and other IDs |

## Notes

- OpenAlex IDs for authors start with `A` (e.g. `A5023888391`).
- Author names are not unique; use ORCID or OpenAlex ID for precise identification.
- The `affiliations` field provides historical institutional data with year ranges.
- `last_known_institutions` is a convenience shortcut for the most recent affiliation.
- The `x_concepts` field is deprecated; use `topics` and `topic_share` instead.
