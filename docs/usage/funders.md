# Funders

`client.funders` talks to the `/funders` endpoint and returns `Funder` models.

```python
funder = await client.funders.get("F4320306100")

page = await client.funders.search(
    {"country_code": "nl"},
    select=["id", "display_name", "awards_count"],
)
```

## Filters

Common `FundersFilters` fields: `display_name`, `country_code`, `continent`, `is_global_south`, `ror`, `works_count`, `works_count_range`, `awards_count`, `display_name.search`, and the summary-stat filters `summary_stats.2yr_mean_citedness`, `summary_stats.h_index`, `summary_stats.i10_index`.

The grant-era field names are gone upstream: the live API returns `awards_count` (not `grants_count`), and `works_api_url` no longer appears on funder objects. All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`.
