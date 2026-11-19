# Publishers

`client.publishers` talks to the `/publishers` endpoint and returns `Publisher` models.

```python
publisher = await client.publishers.get("P4310319900")

page = await client.publishers.search(
    {"hierarchy_level": 0},
    select=["id", "display_name", "works_count"],
)
```

## Filters

Common `PublishersFilters` fields: `display_name`, `country_codes`, `continent`, `hierarchy_level`, `lineage`, `ror`, `works_count`, `works_count_range`, and `display_name.search`.

Publisher hierarchies are trees: `lineage` lists ancestors nearest first, and `hierarchy_level` selects top-level publishers (0) or children. All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`.
