# Sources Endpoint

The Sources endpoint covers journals, repositories, conference proceedings,
ebook platforms, and book series indexed in OpenAlex.

**Endpoint path:** `sources`
**Client access:** `session.sources`

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    async for source in session.sources.iterate(
        filters=SourcesFilters(type="journal", is_oa=True),
    ):
        print(f"{source.display_name} — {source.issn_l}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.sources.get("S123")` | Fetch a single source by OpenAlex ID or ISSN |
| Search | `session.sources.search("Nature")` | Search sources by name |
| Iterate | `session.sources.iterate(filters=...)` | Cursor-based pagination over filtered results |

## SourcesFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `type` | `type` | `str` | Source type: `journal`, `repository`, `conference`, `ebook platform`, `book series` |
| `is_oa` | `is_oa` | `bool` | Whether the source is Open Access |
| `host_organization` | `host_organization` | `str` | OpenAlex ID of the host organization (publisher) |
| `issn` | `issn` | `str` | ISSN (any ISSN associated with the source) |
| `issn_l` | `issn_l` | `str` | Linking ISSN |
| `has_apc` | `has_apc` | `bool` | Whether the source has article processing charges |
| `works_count` | `works_count` | `int` | Exact number of works in this source |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"1000-10000"`) |
| `cited_by_count` | `cited_by_count` | `int` | Exact citation count |
| `cited_by_count_range` | `cited_by_count_range` | `str` | Citation count range (e.g., `"100000-1000000"`) |

### Search & Geographic Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within display names |
| `default_search` | `default.search` | `str` | Default search across multiple fields |
| `continent` | `continent` | `str` | Continent of the source's publisher |
| `has_issn` | `has_issn` | `bool` | Whether the source has an ISSN |
| `is_global_south` | `is_global_south` | `bool` | Whether the source is in the Global South |
| `x_concepts_id` | `x_concepts.id` | `str` | Concept ID (deprecated; prefer topics) |

## Usage Examples

### Find OA journals with an ISSN

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    filters = SourcesFilters(
        type="journal",
        is_oa=True,
        has_issn=True,
    )
    async for source in session.sources.iterate(filters=filters):
        print(f"{source.display_name} — ISSN-L: {source.issn_l}")
```

### Search sources by publisher

```python
async with SynthecaSession() as session:
    filters = SourcesFilters(host_organization="P4310320990")
    async for source in session.sources.iterate(filters=filters):
        print(source.display_name)
```

### Filter by works count range

```python
async with SynthecaSession() as session:
    filters = SourcesFilters(
        type="journal",
        works_count_range="10000-1000000",
    )
    async for source in session.sources.iterate(filters=filters):
        print(f"{source.display_name}: {source.works_count} works")
```
