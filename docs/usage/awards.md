# Awards

`client.awards` talks to the `/awards` endpoint and returns `Award` models (grants, verified against funding sources).

```python
award = await client.awards.get("AW449823")
```

## Filters

`AwardsFilters` is the widest filter model in the library: `id`, `doi`, `funder_name`, `funder_award_id`, `funder_scheme`, `funding_type`, `provenance`, `collection`, `currency`, `amount`, `start_year`, `end_year`, `funded_outputs`, `funded_outputs_count`, and nested fields under `funder.*`, `lead_investigator.*`, and `institution_awarded.*`.

OpenAlex documents only part of these; the full list is discoverable by sending an invalid filter and reading the 400 body (see [upstream quirks](../upstream-quirks.md)). All shared operations are available: `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, `batch_get()`.

## Field shape notes from the live API

- `institution_awarded` is always a list, despite the singular name (often empty).
- `funded_outputs` holds raw OpenAlex work URLs as strings, not objects.
