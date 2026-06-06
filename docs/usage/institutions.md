# Institutions

The Institutions endpoint represents academic and research organizations — universities, research institutes, government agencies, healthcare organizations, and companies. Each institution links to geographic data, associated institutions, publication metrics, and hierarchical lineage.

## Quick Start

### Get an institution by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    institution = await session.institutions.get("I31371856")  # Stanford University
    print(institution.display_name)
    print(institution.type)
    print(institution.country_code)
    print(institution.works_count)
```

### Search for institutions

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.institutions.search(
        search="stanford",
        page_size=10,
    )
    for inst in results.results:
        print(f"{inst.display_name} ({inst.country_code}) — {inst.works_count} works")
```

## Filtering

Use `InstitutionsFilters` to construct structured filter queries:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    filters = InstitutionsFilters(
        country_code="US",
        type="education",
    )
    results = await session.institutions.search(filters=filters, page_size=25)
```

### Filter by country

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    # ISO 3166-1 alpha-2 country codes
    filters = InstitutionsFilters(country_code="DE")  # Germany
    filters = InstitutionsFilters(country_code="JP")  # Japan
    filters = InstitutionsFilters(country_code="BR")  # Brazil

    # By continent
    filters = InstitutionsFilters(continent="europe")

    # Global South
    filters = InstitutionsFilters(is_global_south=True)
```

### Filter by type

Institution types include `education`, `facility`, `healthcare`, `company`, `government`, `nonprofit`, and `archive`:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    # Universities and colleges
    filters = InstitutionsFilters(type="education")

    # Research facilities (e.g. national labs)
    filters = InstitutionsFilters(type="facility")

    # Government agencies
    filters = InstitutionsFilters(type="government")

    # Companies
    filters = InstitutionsFilters(type="company")

    # Healthcare organizations
    filters = InstitutionsFilters(type="healthcare")
```

### Filter by ROR ID

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    filters = InstitutionsFilters(ror="https://ror.org/00f54p054")
    results = await session.institutions.search(filters=filters, page_size=1)
```

### Filter by citation or works count

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    # High-output institutions
    filters = InstitutionsFilters(works_count_range="100000-")

    # Highly cited institutions
    filters = InstitutionsFilters(cited_by_count_range="1000000-")
```

## Associated Institutions

Each institution has an `associated_institutions` list that captures parent/child relationships, predecessor/successor links, and related organizations:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    institution = await session.institutions.get("I31371856")

    for related in institution.associated_institutions:
        print(f"  {related.display_name} — {related.relationship} — {related.id}")
```

The `relationship` field indicates the type of association: `parent`, `child`, `predecessor`, `successor`, `related`, etc.

## Lineage

The `lineage` field provides the full organizational hierarchy as a list of OpenAlex IDs from root to current:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    institution = await session.institutions.get("I31371856")
    print(f"Lineage: {institution.lineage}")
```

## Geographic Data

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    institution = await session.institutions.get("I31371856")

    if institution.geo:
        print(f"City: {institution.geo.city}")
        print(f"Country: {institution.geo.country}")
        print(f"Latitude: {institution.geo.latitude}")
        print(f"Longitude: {institution.geo.longitude}")
```

## Iteration

```python
from aletheca import AlethecaSession
from aletheca.endpoints import InstitutionsFilters

async with AlethecaSession() as session:
    filters = InstitutionsFilters(
        country_code="US",
        type="education",
    )
    async for inst in session.institutions.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{inst.display_name}: {inst.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Institution display name |
| `type` | `str \| None` | `education`, `facility`, `healthcare`, `company`, `government`, `nonprofit`, `archive` |
| `country_code` | `str \| None` | ISO 3166-1 alpha-2 code |
| `geo` | `Geo \| None` | Geographic coordinates and location |
| `associated_institutions` | `list[RelatedInstitution]` | Related organizations with relationship types |
| `lineage` | `list[str]` | Full organizational hierarchy (OpenAlex IDs) |
| `ror` | `str \| None` | ROR (Research Organization Registry) ID |
| `works_count` | `int \| None` | Total number of works |
| `cited_by_count` | `int \| None` | Total citations |
| `roles` | `list[Role]` | Roles the institution plays (funder, publisher, etc.) |
| `repositories` | `list[Repository]` | Associated repositories |
| `homepage_url` | `str \| None` | Institution homepage |
| `display_name_acronyms` | `list[str]` | Common abbreviations |
| `display_name_alternatives` | `list[str]` | Alternative names |
| `counts_by_year` | `list[YearCount]` | Annual works/citations breakdown |
| `summary_stats` | `SummaryStats \| None` | 2yr mean citedness, h-index, i10-index |

## Notes

- OpenAlex IDs for institutions start with `I` (e.g. `I31371856`).
- Institution types: `education`, `facility`, `healthcare`, `company`, `government`, `nonprofit`, `archive`.
- The `lineage` field provides the full hierarchy from root organization to the current one.
- `associated_institutions` includes relationship types (parent, child, predecessor, successor, related).
- Geographic data is available in the `geo` nested object with city, country, latitude, and longitude.
- The `x_concepts` field is deprecated; use `topics` and `topic_share` instead.
