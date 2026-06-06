# Usage Basics

A practical guide to the core syntheca patterns: sessions, entity access, filtering, iteration, and collecting.

## Creating a session

`SynthecaSession` is the main entry point. It manages the underlying HTTP client lifecycle and provides access to all resource endpoints.

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")
    print(work.display_name)
```

Pass an API key or settings explicitly if you don't use environment variables:

```python
async with SynthecaSession(api_key="your-key") as session:
    ...
```

??? note "What happens under the hood?"
    `SynthecaSession` creates a `SynthecaClient` internally, which in turn creates an `httpx.AsyncClient` on first use. Resource clients (works, authors, etc.) are initialized lazily as properties. The `async with` block ensures the HTTP client is properly closed.

## Resource clients

The session exposes eight entity endpoints as attributes:

| Attribute | Entity | Client class |
|---|---|---|
| `session.works` | Works | `WorksClient` |
| `session.authors` | Authors | `AuthorsClient` |
| `session.sources` | Sources | `SourcesClient` |
| `session.institutions` | Institutions | `InstitutionsClient` |
| `session.topics` | Topics | `TopicsClient` |
| `session.keywords` | Keywords | `KeywordsClient` |
| `session.publishers` | Publishers | `PublishersClient` |
| `session.funders` | Funders | `FundersClient` |

## Getting a single entity

Use `.get()` to fetch by OpenAlex ID. The works endpoint also supports DOIs and PMIDs:

```python
async with SynthecaSession() as session:
    # By OpenAlex ID
    work = await session.works.get("W2741809807")

    # By DOI (works only)
    work = await session.works.get("https://doi.org/10.1038/nature12373")

    author = await session.authors.get("A5023888391")
    institution = await session.institutions.get("I31821745")
```

## Searching

Use `.search()` to do a full-text search on an entity:

```python
async with SynthecaSession() as session:
    response = await session.authors.search(search="Elinor Ostrom")
    for author in response.results:
        print(f"{author.display_name} — {author.works_count} works")
```

Paginate with `page` and `per_page` (max 200):

```python
response = await session.works.search(
    search="climate change",
    page=1,
    per_page=50,
)
```

## Filtering with Pydantic models

Each endpoint has a corresponding filter model in `syntheca.endpoints`. These models use Pydantic aliases to map Python-friendly attribute names to OpenAlex dot-notation filter syntax.

```python
from syntheca.endpoints import WorksFilters

filters = WorksFilters(
    publication_year=2024,
    is_oa=True,
    authorships_author_id="A5023888391",  # becomes authorships.author.id:A5023888391
)
```

The filter model serializes to OpenAlex's `filter=key:value,key:value` format automatically.

You can also pass a plain dict for filters:

```python
async for work in session.works.iterate(
    filters={"publication_year": 2024, "type": "article"},
):
    print(work.display_name)
```

### Available filter fields (WorksFilters)

A subset of commonly used filters:

| Python parameter | OpenAlex filter |
|---|---|
| `publication_year` | `publication_year` |
| `is_oa` | `is_oa` |
| `doi` | `doi` |
| `type` | `type` |
| `authorships_author_id` | `authorships.author.id` |
| `authorships_institutions_id` | `authorships.institutions.id` |
| `topics_id` | `topics.id` |
| `primary_location_source_id` | `primary_location.source.id` |
| `has_doi` | `has_doi` |
| `default_search` | `default.search` |
| `title_and_abstract_search` | `title_and_abstract.search` |

!!! tip "Extra fields are allowed"
    All filter models use `extra="allow"`, so you can pass any filter key OpenAlex supports — even ones not explicitly defined on the model.

## Iterating with cursor pagination

For large result sets, use `.iterate()` which yields individual entities via OpenAlex cursor pagination:

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters


async def all_oa_articles():
    async with SynthecaSession() as session:
        filters = WorksFilters(is_oa=True, type="article", publication_year=2024)
        count = 0
        async for work in session.works.iterate(filters=filters, per_page=200):
            count += 1
            if count > 500:
                break
        print(f"Processed {count} works")
```

The `per_page` parameter defaults to 200 (the OpenAlex maximum) for iteration.

## Collecting into a list

When you need all results in memory, use `.collect()`:

```python
async with SynthecaSession() as session:
    works = await session.works.collect(
        filters={"authorships.author.id": "A5023888391"},
        limit=50,
    )
    print(f"Collected {len(works)} works")
```

!!! warning "Memory usage"
    `.collect()` materializes all results into a list. For queries returning thousands of results, prefer `.iterate()` to process items one at a time.

## Sorting

Pass `sort` as `field:direction`:

```python
async with SynthecaSession() as session:
    response = await session.works.search(
        search="quantum computing",
        sort="cited_by_count:desc",
        per_page=10,
    )
```

## Convenience queries

`session.queries` provides higher-level functions that compose multiple API calls:

```python
async with SynthecaSession() as session:
    # Works by author name (looks up author ID, then fetches works)
    works = await session.queries.works_by_author("Elinor Ostrom", limit=20)

    # Works affiliated with an institution
    works = await session.queries.works_by_institution("MIT", limit=50)

    # Fetch works by DOI
    works = await session.queries.works_by_doi([
        "10.1038/nature12373",
        "10.1126/science.1157996",
    ])

    # Citing and referenced works
    citing = await session.queries.citing_works("W2741809807", limit=100)
    refs = await session.queries.referenced_works("W2741809807", limit=100)
```
