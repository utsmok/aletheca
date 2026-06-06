# Funders

The Funders endpoint represents organizations that fund research — government agencies, foundations, and other funding bodies. Each funder links to their awarded grants, country, and publication metrics for funded works.

## Quick Start

### Get a funder by OpenAlex ID

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    funder = await session.funders.get("F4320332161")  # NIH
    print(funder.display_name)
    print(funder.country_code)
    print(funder.works_count)
    print(funder.awards_count)
```

### Search for funders

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    results = await session.funders.search(
        search="national science foundation",
        page_size=10,
    )
    for funder in results.results:
        print(f"{funder.display_name} ({funder.country_code}): {funder.awards_count} awards")
```

## Filtering

Use `FundersFilters` to construct structured filter queries:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    filters = FundersFilters(
        country_code="US",
    )
    results = await session.funders.search(filters=filters, page_size=25)
```

### Filter by country

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    # US-based funders (NIH, NSF, DOE, etc.)
    filters = FundersFilters(country_code="US")

    # UK-based funders (UKRI, Wellcome Trust, etc.)
    filters = FundersFilters(country_code="GB")

    # EU-based funders
    filters = FundersFilters(country_code="EU")
```

### Filter by ROR ID

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    filters = FundersFilters(ror="https://ror.org/01cwqze88")
    results = await session.funders.search(filters=filters, page_size=1)
```

### Filter by awards count

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    # Major funders with many awards
    filters = FundersFilters(works_count_range="100000-")

    # Funders with a specific number of awards
    filters = FundersFilters(awards_count=5000)
```

### Filter by works count

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    # Funders whose funded outputs have high citation impact
    filters = FundersFilters(works_count_range="50000-")
```

## Iteration

```python
from syntheca import SynthecaSession
from syntheca.endpoints import FundersFilters

async with SynthecaSession() as session:
    filters = FundersFilters(
        country_code="US",
        works_count_range="10000-",
    )
    async for funder in session.funders.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{funder.display_name}: {funder.works_count} works, {funder.awards_count} awards")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Funder display name |
| `country_code` | `str \| None` | ISO 3166-1 alpha-2 country code |
| `description` | `str \| None` | Funder description |
| `awards_count` | `int \| None` | Number of awards granted |
| `works_count` | `int \| None` | Number of works acknowledging this funder |
| `cited_by_count` | `int \| None` | Citations to works from this funder |
| `alternate_titles` | `list[str]` | Alternative names for the funder |
| `homepage_url` | `str \| None` | Funder homepage |
| `roles` | `list[Role]` | Roles the funder plays |
| `counts_by_year` | `list[YearCount]` | Annual works/citations breakdown |
| `summary_stats` | `SummaryStats \| None` | 2yr mean citedness, h-index, i10-index |

## Live API Notes

- The OpenAPI spec lists `grants_count` and `works_api_url` on Funder objects, but the live API returns `awards_count` instead and does not include `works_api_url`. Syntheca follows the live API.
- The `awards_count` field reflects the transition from "grants" to "awards" terminology in OpenAlex.

## Notes

- OpenAlex IDs for funders start with `F` (e.g. `F4320332161`).
- The `awards_count` field shows how many individual awards/grants the funder has in OpenAlex.
- Not all funded works have explicit award records; `works_count` may exceed what's traceable through individual awards.
- Funders can have multiple `roles` — they may simultaneously be a funder and publisher.
- Use the Awards endpoint to drill into individual award records for a specific funder.
