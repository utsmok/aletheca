# Keywords

The Keywords endpoint represents keywords extracted from scholarly works. Keywords are single- or multi-word terms that capture the key topics and themes of a work. They are assigned automatically and provide a more granular classification than the topic hierarchy.

## Quick Start

### Get a keyword by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    keyword = await session.keywords.get("K123456")
    print(keyword.display_name)
    print(keyword.works_count)
    print(keyword.cited_by_count)
```

### Search for keywords

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.keywords.search(
        search="neural network",
        page_size=10,
    )
    for kw in results.results:
        print(f"{kw.display_name}: {kw.works_count} works")
```

## Filtering

Use `KeywordsFilters` to construct structured filter queries:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    filters = KeywordsFilters(
        display_name_search="deep learning",
    )
    results = await session.keywords.search(filters=filters, page_size=25)
```

### Filter by works count

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    # Popular keywords (many associated works)
    filters = KeywordsFilters(works_count_range="10000-")
    results = await session.keywords.search(filters=filters, page_size=50)

    # Exact count
    filters = KeywordsFilters(works_count=500)
```

### Filter by display name

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    # Exact display name match
    filters = KeywordsFilters(display_name="machine learning")

    # Search (partial match)
    filters = KeywordsFilters(display_name_search="machine")
```

## Iteration

```python
from aletheca import AlethecaSession
from aletheca.endpoints import KeywordsFilters

async with AlethecaSession() as session:
    filters = KeywordsFilters(works_count_range="1000-")
    async for keyword in session.keywords.iterate(
        filters=filters,
        per_page=100,
        sort="works_count:desc",
    ):
        print(f"{keyword.display_name}: {keyword.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Keyword text |
| `works_count` | `int \| None` | Number of works tagged with this keyword |
| `cited_by_count` | `int \| None` | Total citations for associated works |
| `works_api_url` | `str \| None` | URL to fetch works with this keyword |
| `created_date` | `str \| None` | Date the keyword was created in OpenAlex |
| `updated_date` | `str \| None` | Date the keyword was last updated |

## Notes

- OpenAlex IDs for keywords start with `K` (e.g. `K123456`).
- Keywords are automatically extracted from works using NLP techniques.
- Keywords provide a more granular classification than the domain/field/subfield/topic hierarchy.
- The `works_count` field is useful for finding popular or trending research keywords.
- Use `works_count_range` with range syntax (e.g. `"100-1000"`, `"10000-"`) to filter by count brackets.
