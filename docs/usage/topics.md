# Topics

`client.topics` talks to the `/topics` endpoint and returns `Topic` models. OpenAlex assigns every work exactly one primary topic, arranged in a `subfield > field > domain` hierarchy.

```python
topic = await client.topics.get("T10100")

page = await client.topics.search(
    {"field.id": "fields/17"},
    select=["id", "display_name", "works_count"],
)
```

## Filters

Common `TopicsFilters` fields: `display_name`, `id`, `subfield.id`, `field.id`, `domain.id`, `works_count`, `works_count_range`, `display_name.search`, and the keyword filters `keywords.id`, `keywords.search`, `keywords.keyword`, `keywords.display_name`.

All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`. `Topic.siblings` holds related topics as returned by the live API.
