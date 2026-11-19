# Sources

`client.sources` talks to the `/sources` endpoint and returns `Source` models (journals, repositories, conference proceedings).

```python
source = await client.sources.get("S137773608")

page = await client.sources.search(
    {"is_oa": True, "continent": "europe"},
    select=["id", "display_name", "host_organization"],
)
```

## Filters

Common `SourcesFilters` fields: `display_name`, `type`, `is_oa`, `host_organization`, `issn`, `issn_l`, `has_apc`, `has_issn`, `is_global_south`, `continent`, `works_count`, `works_count_range`, `cited_by_count`, `cited_by_count_range`, `display_name.search`, and the summary-stat filters `summary_stats.2yr_mean_citedness`, `summary_stats.h_index`, `summary_stats.i10_index`.

ISSN values are not normalized client-side; pass them in the form OpenAlex expects (`0472-9092`, or the `S...` id under `host_organization`).

All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`.
