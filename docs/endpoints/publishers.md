# Publishers Endpoint

The Publishers endpoint provides access to publisher records in OpenAlex —
organizations that publish academic journals, books, and other scholarly content.

**Endpoint path:** `publishers`
**Client access:** `session.publishers`

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    async for pub in session.publishers.iterate(
        filters=PublishersFilters(country_codes="US"),
    ):
        print(f"{pub.display_name} — {pub.works_count} works")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.publishers.get("P123")` | Fetch a single publisher by OpenAlex ID |
| Search | `session.publishers.search("Springer")` | Search publishers by name |
| Iterate | `session.publishers.iterate(filters=...)` | Cursor-based pagination over filtered results |

## PublishersFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `country_codes` | `country_codes` | `str` | Country code(s) where the publisher operates. Pipe-delimited for multiple. |
| `hierarchy_level` | `hierarchy_level` | `int` | Level in the publisher hierarchy (0 = top-level) |
| `works_count` | `works_count` | `int` | Exact number of works published |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"1000-100000"`) |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within publisher display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

## Usage Examples

### Find publishers in specific countries

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    filters = PublishersFilters(country_codes="GB|NL")
    async for pub in session.publishers.iterate(filters=filters):
        print(f"{pub.display_name} — {pub.hierarchy_level}")
```

### Search for a publisher by name

```python
async with AlethecaSession() as session:
    filters = PublishersFilters(display_name_search="Elsevier")
    async for pub in session.publishers.iterate(filters=filters):
        print(f"{pub.display_name}: {pub.works_count} works")
```

### Large publishers by work count

```python
async with AlethecaSession() as session:
    filters = PublishersFilters(
        works_count_range="100000-10000000",
        hierarchy_level=0,
    )
    async for pub in session.publishers.iterate(
        filters=filters,
        sort_by="works_count:desc",
    ):
        print(f"{pub.display_name}: {pub.works_count}")
```
