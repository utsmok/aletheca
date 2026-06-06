# Topics Endpoint

The Topics endpoint provides access to OpenAlex topics — a hierarchical classification
system that groups works by subject area. Topics are organized into domains, fields,
and subfields.

**Endpoint path:** `topics`
**Client access:** `session.topics`

```python
from syntheca import SynthecaSession
from syntheca.endpoints import TopicsFilters

async with SynthecaSession() as session:
    async for topic in session.topics.iterate(
        filters=TopicsFilters(field_id="F1"),
    ):
        print(f"{topic.display_name} — {topic.subfield.display_name if topic.subfield else 'N/A'}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.topics.get("T123")` | Fetch a single topic by OpenAlex ID |
| Search | `session.topics.search("machine learning")` | Search topics by name |
| Iterate | `session.topics.iterate(filters=...)` | Cursor-based pagination over filtered results |

## TopicsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `id` | `id` | `str` | OpenAlex Topic ID |
| `subfield_id` | `subfield_id` | `str` | Subfield ID to filter topics belonging to a specific subfield |
| `field_id` | `field_id` | `str` | Field ID to filter topics belonging to a specific field |
| `domain_id` | `domain_id` | `str` | Domain ID to filter topics belonging to a specific domain |
| `works_count` | `works_count` | `int` | Exact number of works tagged with this topic |
| `works_count_range` | `works_count_range` | `str` | Works count range (e.g., `"1000-10000"`) |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within topic display names |
| `keywords_keyword` | `keywords.keyword` | `str` | Filter by a keyword associated with the topic |

## Usage Examples

### Find topics in a specific field

```python
from syntheca import SynthecaSession
from syntheca.endpoints import TopicsFilters

async with SynthecaSession() as session:
    filters = TopicsFilters(field_id="F3")
    async for topic in session.topics.iterate(filters=filters):
        print(f"{topic.display_name} — {topic.works_count} works")
```

### Search topics by keyword

```python
async with SynthecaSession() as session:
    filters = TopicsFilters(keywords_keyword="deep learning")
    async for topic in session.topics.iterate(filters=filters):
        print(topic.display_name)
```

### Get a single topic by ID

```python
async with SynthecaSession() as session:
    topic = await session.topics.get("T10100")
    print(f"{topic.display_name}: {topic.description}")
```
