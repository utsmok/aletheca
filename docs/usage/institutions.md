# Institutions

`client.institutions` talks to the `/institutions` endpoint and returns `Institution` models.

```python
utwente = await client.institutions.get("I1290904741")

page = await client.institutions.search(
    {"country_code": "nl", "type": "education"},
    select=["id", "display_name", "status"],
)
```

## Filters

Common `InstitutionsFilters` fields: `display_name`, `country_code`, `type`, `ror`, `continent`, `is_global_south`, `has_ror`, `is_super_system`, `works_count`, `works_count_range`, `cited_by_count`, `cited_by_count_range`, and `display_name.search`.

## Working with associated institutions

`Institution.associated_institutions` accepts any relationship value (including `predecessor`), matching what the live API returns. `Institution.lineage` lists the institution and its ancestors nearest first; filter on it with `{"affiliations.institution.lineage": ror_or_id}`.

All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`.
