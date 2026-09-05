# Keywords Endpoint

The Keywords endpoint provides access to keywords — single-word or short-phrase
tags associated with OpenAlex topics and works.

**Endpoint path:** `keywords`
**Client access:** `session.keywords`

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    async for kw in session.keywords.iterate(
        filters=KeywordsFilters(display_name_search="quantum"),
    ):
        print(f"{kw.display_name} — {kw.works_count} works")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.keywords.get("K123")` | Fetch a single keyword by OpenAlex ID |
| Search | `session.keywords.search("machine")` | Search keywords by name |
| Iterate | `session.keywords.iterate(filters=...)` | Cursor-based pagination over filtered results |

## KeywordsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `works_count` | `works_count` | `int` | Exact number of works associated with this keyword |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"100-1000"`) |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within keyword display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

## Usage Examples

### Search keywords

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    filters = KeywordsFilters(display_name_search="neural network")
    async for kw in session.keywords.iterate(filters=filters):
        print(f"{kw.display_name}: {kw.works_count} works")
```

### Find popular keywords by work count

```python
async with AlethecaSession() as session:
    filters = KeywordsFilters(works_count_range="10000-1000000")
    async for kw in session.keywords.iterate(
        filters=filters,
        sort_by="works_count:desc",
    ):
        print(f"{kw.display_name}: {kw.works_count}")
```
