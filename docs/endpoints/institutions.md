# Institutions Endpoint

The Institutions endpoint provides access to institutional records — universities,
research centers, government agencies, companies, and other organizations tracked
in OpenAlex.

**Endpoint path:** `institutions`
**Client access:** `session.institutions`

```python
from syntheca import SynthecaSession
from syntheca.endpoints import InstitutionsFilters

async with SynthecaSession() as session:
    async for inst in session.institutions.iterate(
        filters=InstitutionsFilters(country_code="US", type="education"),
    ):
        print(f"{inst.display_name} — {inst.ror}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.institutions.get("I123")` | Fetch a single institution by OpenAlex ID or ROR |
| Search | `session.institutions.search("MIT")` | Search institutions by name |
| Iterate | `session.institutions.iterate(filters=...)` | Cursor-based pagination over filtered results |

## InstitutionsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `country_code` | `country_code` | `str` | ISO 3166-1 alpha-2 country code (e.g., `"US"`, `"DE"`, `"JP"`) |
| `type` | `type` | `str` | Institution type: `education`, `facility`, `healthcare`, `company`, `archive`, `nonprofit`, `government`, `other` |
| `ror` | `ror` | `str` | ROR (Research Organization Registry) ID |
| `works_count` | `works_count` | `int` | Exact number of works |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"1000-10000"`) |
| `cited_by_count` | `cited_by_count` | `int` | Exact citation count |
| `cited_by_count_range` | `cited_by_count_range` | `str` | Citation count range |

### Search & Geographic Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |
| `continent` | `continent` | `str` | Continent name |
| `is_global_south` | `is_global_south` | `bool` | Whether the institution is in the Global South |

## Usage Examples

### Find universities in a country

```python
from syntheca import SynthecaSession
from syntheca.endpoints import InstitutionsFilters

async with SynthecaSession() as session:
    filters = InstitutionsFilters(
        country_code="GB",
        type="education",
    )
    async for inst in session.institutions.iterate(filters=filters):
        print(f"{inst.display_name} — works: {inst.works_count}")
```

### Look up institution by ROR

```python
async with SynthecaSession() as session:
    inst = await session.institutions.get("https://ror.org/0130frc33")
    print(inst.display_name)
```

### Find institutions in the Global South with many works

```python
async with SynthecaSession() as session:
    filters = InstitutionsFilters(
        is_global_south=True,
        works_count_range="10000-1000000",
    )
    async for inst in session.institutions.iterate(filters=filters):
        print(f"{inst.display_name} ({inst.country_code}): {inst.works_count} works")
```
