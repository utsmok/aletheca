# Sources

The Sources endpoint represents venues where scholarly works are published — journals, conference proceedings, repositories, and ebook platforms. Each source links to its publisher, APC pricing, ISSN identifiers, and metadata about the works it contains.

## Quick Start

### Get a source by OpenAlex ID

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    source = await session.sources.get("S137030756")  # Nature
    print(source.display_name)
    print(source.type)  # "journal"
    print(source.issn)
    print(source.is_oa)
```

### Search for sources

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    results = await session.sources.search(
        search="nature communications",
        page_size=10,
    )
    for source in results.results:
        print(f"{source.display_name} ({source.type})")
```

## Filtering

Use `SourcesFilters` to construct structured filter queries:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    filters = SourcesFilters(
        type="journal",
        is_oa=True,
    )
    results = await session.sources.search(filters=filters, page_size=25)
```

### Filter by type

Source types include `journal`, `repository`, `conference`, `ebook platform`, and `book series`:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Journals only
    filters = SourcesFilters(type="journal")

    # Conference proceedings
    filters = SourcesFilters(type="conference")

    # Repositories (e.g. arXiv, bioRxiv)
    filters = SourcesFilters(type="repository")

    # Ebook platforms
    filters = SourcesFilters(type="ebook platform")
```

### ISSN lookup

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Look up by specific ISSN
    filters = SourcesFilters(issn="0028-0836")  # Nature
    results = await session.sources.search(filters=filters, page_size=1)
    if results.results:
        print(results.results[0].display_name)

    # Look up by ISSN-L (linking ISSN)
    filters = SourcesFilters(issn_l="0028-0836")

    # Filter to sources that have an ISSN
    filters = SourcesFilters(has_issn=True)
```

### Filter by APC data

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Sources that charge an APC
    filters = SourcesFilters(has_apc=True, type="journal")
    results = await session.sources.search(filters=filters, page_size=25)
    for source in results.results:
        print(f"{source.display_name}: ${source.apc_usd}")

    # Access detailed APC pricing
    source = await session.sources.get("S137030756")
    for price in source.apc_prices:
        print(f"  {price.currency}: {price.price}")
```

### Filter by open access status

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Fully open access journals
    filters = SourcesFilters(is_oa=True, type="journal")

    # Journals indexed in DOAJ
    source = await session.sources.get("S137030756")
    print(source.is_in_doaj)
```

### Filter by host organization (publisher)

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Sources from a specific publisher
    filters = SourcesFilters(host_organization="P4310320990")  # Springer Nature
    results = await session.sources.search(filters=filters, page_size=25)
```

### Filter by geography

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    # Sources from the Global South
    filters = SourcesFilters(is_global_south=True)

    # Sources from a specific continent
    filters = SourcesFilters(continent="europe")
```

## Iteration

```python
from syntheca import SynthecaSession
from syntheca.endpoints import SourcesFilters

async with SynthecaSession() as session:
    filters = SourcesFilters(
        type="journal",
        is_oa=True,
        works_count_range="1000-",
    )
    async for source in session.sources.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{source.display_name}: {source.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Source display name |
| `type` | `str \| None` | `journal`, `repository`, `conference`, `ebook platform`, `book series` |
| `issn` | `list[str]` | ISSN identifiers |
| `issn_l` | `str \| None` | Linking ISSN |
| `is_oa` | `bool \| None` | Whether fully open access |
| `is_in_doaj` | `bool \| None` | Whether indexed in DOAJ |
| `apc_usd` | `int \| None` | Article processing charge in USD |
| `apc_prices` | `list[APCEntry]` | Detailed APC pricing by currency |
| `host_organization` | `str \| None` | Publisher OpenAlex ID |
| `host_organization_name` | `str \| None` | Publisher display name |
| `host_organization_lineage` | `list[str]` | Publisher lineage (parent orgs) |
| `works_count` | `int \| None` | Total number of works |
| `cited_by_count` | `int \| None` | Total citations |
| `country_code` | `str \| None` | ISO country code |
| `homepage_url` | `str \| None` | Source homepage |
| `societies` | `list[Society]` | Associated academic societies |
| `counts_by_year` | `list[YearCount]` | Annual works/citations breakdown |

## Notes

- OpenAlex IDs for sources start with `S` (e.g. `S137030756`).
- Source types: `journal`, `repository`, `conference`, `ebook platform`, `book series`.
- APC data is available via `apc_usd` (single value) and `apc_prices` (detailed list).
- `host_organization` links to the publisher entity; `host_organization_lineage` traces parent publishers.
- The `is_in_doaj` flag indicates whether the journal is in the Directory of Open Access Journals.
- The `x_concepts` field is deprecated; use `topics` and `topic_share` instead.
