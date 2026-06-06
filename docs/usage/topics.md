# Topics

The Topics endpoint represents the OpenAlex topic classification system — a three-level hierarchy of domains, fields, and subfields that categorize scholarly works. Topics are assigned to works automatically based on their content.

## Quick Start

### Get a topic by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    topic = await session.topics.get("T10001")  # Example topic
    print(topic.display_name)
    print(topic.description)
    print(topic.works_count)
    print(topic.keywords)
```

### Search for topics

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.topics.search(
        search="machine learning",
        page_size=10,
    )
    for topic in results.results:
        print(f"{topic.display_name}: {topic.works_count} works")
```

## Filtering

Use `TopicsFilters` to construct structured filter queries:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import TopicsFilters

async with AlethecaSession() as session:
    filters = TopicsFilters(
        display_name_search="climate",
        works_count_range="10000-",
    )
    results = await session.topics.search(filters=filters, page_size=25)
```

### Filter by hierarchy level

The OpenAlex topic hierarchy has three levels: **domain** → **field** → **subfield**. Each topic belongs to one subfield, which belongs to one field, which belongs to one domain:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import TopicsFilters

async with AlethecaSession() as session:
    # All topics in a specific domain
    filters = TopicsFilters(domain_id="D1")  # Physical Sciences

    # All topics in a specific field
    filters = TopicsFilters(field_id="F1")  # Computer Science

    # All topics in a specific subfield
    filters = TopicsFilters(subfield_id="SF1")  # Artificial Intelligence
```

### Filter by keyword

```python
from aletheca import AlethecaSession
from aletheca.endpoints import TopicsFilters

async with AlethecaSession() as session:
    # Topics that contain a specific keyword
    filters = TopicsFilters(keywords_keyword="neural networks")
    results = await session.topics.search(filters=filters, page_size=25)
```

### Filter by works count

```python
from aletheca import AlethecaSession
from aletheca.endpoints import TopicsFilters

async with AlethecaSession() as session:
    # Popular topics (100k+ works)
    filters = TopicsFilters(works_count_range="100000-")

    # Exact count
    filters = TopicsFilters(works_count=5000)
```

## Topic Hierarchy

Each topic provides its full hierarchy context through nested objects:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    topic = await session.topics.get("T10001")

    # Subfield
    if topic.subfield:
        print(f"Subfield: {topic.subfield.display_name} ({topic.subfield.id})")

    # Field
    if topic.field:
        print(f"Field: {topic.field.display_name} ({topic.field.id})")

    # Domain
    if topic.domain:
        print(f"Domain: {topic.domain.display_name} ({topic.domain.id})")
```

### Sibling topics

The `siblings` field lists topics within the same subfield:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    topic = await session.topics.get("T10001")

    print("Related topics in the same subfield:")
    for sibling in topic.siblings:
        print(f"  {sibling.display_name} ({sibling.id})")
```

## Iteration

```python
from aletheca import AlethecaSession
from aletheca.endpoints import TopicsFilters

async with AlethecaSession() as session:
    filters = TopicsFilters(
        domain_id="D1",
        works_count_range="50000-",
    )
    async for topic in session.topics.iterate(
        filters=filters,
        per_page=200,
        sort="works_count:desc",
    ):
        print(f"{topic.display_name}: {topic.works_count} works")
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Topic display name |
| `description` | `str \| None` | Topic description |
| `keywords` | `list[str]` | Keywords associated with this topic |
| `subfield` | `Subfield \| None` | Parent subfield |
| `field` | `FieldEntity \| None` | Parent field |
| `domain` | `Domain \| None` | Parent domain |
| `siblings` | `list[TopicMinimal]` | Topics in the same subfield |
| `works_count` | `int \| None` | Total number of works in this topic |
| `cited_by_count` | `int \| None` | Total citations for works in this topic |
| `works_api_url` | `str \| None` | URL to fetch works for this topic |

## Notes

- OpenAlex IDs for topics start with `T` (e.g. `T10001`).
- The hierarchy is three levels: domain → field → subfield → topic.
- Each topic has `domain`, `field`, and `subfield` nested objects providing full context.
- Keywords are automatically extracted and associated with topics.
- The `siblings` field provides a quick way to explore related topics within the same subfield.
- Topics are assigned to works automatically based on machine learning classification.
