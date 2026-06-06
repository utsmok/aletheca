# Publishers

The Publishers endpoint represents publishing organizations — commercial publishers, university presses, scholarly societies, and platform hosts. Publishers own or operate sources (journals, conference proceedings, repositories) and are organized in a hierarchy with parent and child relationships.

## Quick Start

### Get a publisher by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    publisher = await session.publishers.get("P4310320990")  # Springer Nature
    print(publisher.display_name)
    print(publisher.hierarchy_level)
    print(publisher.works_count)
```

### Search for publishers

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.publishers.search(
        search="elsevier",
        page_size=10,
    )
    for pub in results.results:
        print(f"{pub.display_name}: {pub.works_count} works")
```

## Filtering

Use `PublishersFilters` to construct structured filter queries:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    filters = PublishersFilters(
        display_name_search="springer",
    )
    results = await session.publishers.search(filters=filters, page_size=25)
```

### Filter by country

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    # Publishers based in specific countries
    filters = PublishersFilters(country_codes="US")
    filters = PublishersFilters(country_codes="NL")  # Netherlands (Elsevier)
```

### Filter by hierarchy level

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    # Top-level publishers only
    filters = PublishersFilters(hierarchy_level=0)
    results = await session.publishers.search(filters=filters, page_size=25)
```

### Filter by works count

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    # Major publishers
    filters = PublishersFilters(works_count_range="1000000-")
    results = await session.publishers.search(
        filters=filters,
        page_size=25,
        sort="works_count:desc",
    )
```

## Publisher Hierarchy and Lineage

Publishers are organized in a hierarchy. The `lineage` field provides the full chain from root publisher to current, and `parent_publisher` links to the immediate parent:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    publisher = await session.publishers.get("P4310320990")

    # Hierarchy level (0 = top-level)
    print(f"Level: {publisher.hierarchy_level}")

    # Full lineage (list of OpenAlex IDs from root to current)
    print(f"Lineage: {publisher.lineage}")

    # Direct parent
    if publisher.parent_publisher:
        print(f"Parent: {publisher.parent_publisher.get('display_name')}")
```

### Walk the hierarchy

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    # Get all child publishers of a parent
    parent = await session.publishers.get("P4310320554")  # A top-level publisher

    # Search for publishers in the same lineage
    for lineage_id in parent.lineage:
        child = await session.publishers.get(lineage_id)
        print(f"  {child.display_name} (level {child.hierarchy_level})")
```

## Iteration

```python
from aletheca import AlethecaSession
from aletheca.endpoints import PublishersFilters

async with AlethecaSession() as session:
    filters = PublishersFilters(
        hierarchy_level=0,
        works_count_range="100000-",
    )
    async for publisher in session.publishers.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{publisher.display_name}: {publisher.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Publisher display name |
| `hierarchy_level` | `int \| None` | Level in hierarchy (0 = top-level) |
| `parent_publisher` | `ParentPublisher \| None` | Immediate parent publisher as `{id, display_name}` object (not a string) |
| `lineage` | `list[str]` | Full hierarchy chain (OpenAlex IDs, root to current) |
| `country_codes` | `list[str]` | ISO country codes |
| `alternate_titles` | `list[str]` | Alternative publisher names |
| `sources_api_url` | `str \| None` | URL to fetch sources from this publisher |
| `works_count` | `int \| None` | Total number of works |
| `cited_by_count` | `int \| None` | Total citations |
| `roles` | `list[Role]` | Roles the publisher plays |
| `homepage_url` | `str \| None` | Publisher homepage |
| `counts_by_year` | `list[YearCount]` | Annual works/citations breakdown |
| `summary_stats` | `SummaryStats \| None` | 2yr mean citedness, h-index, i10-index |

## Notes

- OpenAlex IDs for publishers start with `P` (e.g. `P4310320990`).
- The publisher hierarchy uses `parent_publisher` for the immediate parent and `lineage` for the full chain.
- `hierarchy_level` is 0 for top-level publishers and increments for each level down.
- The `sources_api_url` field provides a direct link to query sources (journals, etc.) published by this entity.
- Publishers can have multiple `roles` — they may simultaneously be a publisher, funder, or other entity type.
