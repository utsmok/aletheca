# Authors

`client.authors` talks to the `/authors` endpoint and returns `Author` models. It supports `get()`, `search()`, `iterate()`, `collect()`, `first()`, `count()`, and `batch_get()`.

```python
author = await client.authors.get("A5089275346")

page = await client.authors.search(
    {"last_known_institutions.id": "I1290904741"},
    query="ed humburg",
    select=["id", "display_name"],
)
```

## Filters

Common `AuthorsFilters` fields: `orcid`, `display_name`, `works_count`, `cited_by_count`, `has_orcid`, `topics.id`, `affiliations.institution.id`, `last_known_institutions.id`, `last_known_institutions.country_code`, `last_known_institutions.lineage`, `last_known_institutions.ror`, `last_known_institutions.type`, `affiliations.institution.country_code`, `affiliations.institution.lineage`, `affiliations.institution.ror`, `affiliations.institution.type`, and `display_name.search`.

## Batch retrieval

```python
authors = await client.authors.batch_get_by_openalex_id(["A5089275346", "A5023888"])
```

Or the generic form: `client.authors.batch_get(ids, field="openalex")`. Ids are deduplicated, split into chunks of 100 (OpenAlex's OR cap), fetched concurrently, and returned as `dict[normalized id, Author]`.

## Finding works of an author

```python
author = await client.authors.get("A5089275346")
async for work in client.works.iterate({"authorships.author.id": author.id}):
    ...
```

OpenAlex has no works-by-author join, so resolve the author first and filter works by `authorships.author.id`.
