# Funders Endpoint

The Funders endpoint provides access to funding organizations — research councils,
foundations, government agencies, and other entities that fund scholarly research.

**Endpoint path:** `funders`
**Client access:** `session.funders`

```python
from aletheca import AlethecaSession
from aletheca.endpoints import FundersFilters

async with AlethecaSession() as session:
    async for funder in session.funders.iterate(
        filters=FundersFilters(country_code="US"),
    ):
        print(f"{funder.display_name} — {funder.works_count} works funded")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.funders.get("F123")` | Fetch a single funder by OpenAlex ID |
| Search | `session.funders.search("NIH")` | Search funders by name |
| Iterate | `session.funders.iterate(filters=...)` | Cursor-based pagination over filtered results |

## FundersFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `country_code` | `country_code` | `str` | ISO 3166-1 alpha-2 country code (e.g., `"US"`, `"GB"`) |
| `ror` | `ror` | `str` | ROR (Research Organization Registry) ID |
| `works_count` | `works_count` | `int` | Exact number of works funded |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"1000-100000"`) |
| `awards_count` | `awards_count` | `int` | Exact number of awards granted |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within funder display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

## Usage Examples

### Find funders by country

```python
from aletheca import AlethecaSession
from aletheca.endpoints import FundersFilters

async with AlethecaSession() as session:
    filters = FundersFilters(country_code="DE")
    async for funder in session.funders.iterate(filters=filters):
        print(f"{funder.display_name} — {funder.awards_count} awards")
```

### Search for a funder by name

```python
async with AlethecaSession() as session:
    filters = FundersFilters(display_name_search="National Science Foundation")
    async for funder in session.funders.iterate(filters=filters):
        print(f"{funder.display_name} ({funder.country_code})")
```

### Find major funders by ROR

```python
async with AlethecaSession() as session:
    funder = await session.funders.get("https://ror.org/012tx4f57")
    print(f"{funder.display_name}: {funder.works_count} works, {funder.awards_count} awards")
```
