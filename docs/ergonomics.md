# Features & Ergonomics

Syntheca adds convenience features on top of the raw OpenAlex API responses: safe field access, iterator helpers, convenience queries, and OpenAlex-specific utilities.

## Safe Field Access

API responses often have missing fields. Syntheca ensures common field types never return None:

- **List fields** (`authorships`, `concepts`, `locations`, etc.) always return a list — empty instead of None
- **String fields** (`display_name`, `title`, `doi`, etc.) always return a string — empty instead of None

```python
# Iterate without null checks
for authorship in work.authorships:       # always a list
    print(authorship.author.display_name)   # always a string

# String methods just work
work.title.upper()            # safe even if empty

# len(), indexing, etc. — no guards needed
num_ids = len(work.ids.openalex)
```

<iframe src="https://marimo.app/github/utsmok/aletheca/blob/main/examples/08_safe_types_and_helpers.py/wasm?embed=true&mode=read" sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms" style="width:100%;height:500px;border:none;border-radius:8px;"></iframe>

## Iterator Helpers

Every resource client provides three helpers on top of iterate():

```python
async with SynthecaSession() as session:
    # Collect into a list
    papers = await session.works.collect(filters=f, limit=100)

    # Count without downloading
    total = await session.works.count(filters=f)

    # Grab the top result
    top = await session.works.first(filters=f, sort_by="cited_by_count:desc")
```

<iframe src="https://marimo.app/github/utsmok/aletheca/blob/main/examples/07_iterator_helpers.py/wasm?embed=true&mode=read" sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms" style="width:100%;height:500px;border:none;border-radius:8px;"></iframe>

## Convenience Queries

`session.queries` exposes pre-built functions for common research workflows:

| Function | Description |
|---|---|
| `works_by_author(name, limit)` | Fetch works by an author name |
| `works_by_institution(name, limit)` | Works affiliated with an institution |
| `works_by_doi(*dois)` | Fetch works matching DOIs |
| `citing_works(work_id, limit)` | Works citing a given work |
| `referenced_works(work_id, limit)` | Works referenced by a given work |

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    papers = await session.queries.works_by_doi("10.1038/s41586-024-07386-0")
    works = await session.queries.works_by_author("John Smith", limit=50)
    citations = await session.queries.citing_works("W2741809807")
```

<iframe src="https://marimo.app/github/utsmok/aletheca/blob/main/examples/06_convenience_queries.py/wasm?embed=true&mode=read" sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms" style="width:100%;height:500px;border:none;border-radius:8px;"></iframe>

## OpenAlex-Specific Helpers

```python
from syntheca._helpers import normalize_doi, parse_openalex_id, reconstruct_abstract, detect_id_type

# DOI normalization
normalize_doi("https://doi.org/10.1234/test")  # "10.1234/test"

# OpenAlex ID parsing
parse_openalex_id("https://openalex.org/W2741809807")  # "W2741809807"

# Abstract reconstruction from inverted index
abstract = reconstruct_abstract(work.abstract_inverted_index)

# Identifier type detection
detect_id_type("10.1234/test")  # "doi"
detect_id_type("W2741809807")   # "openalex"
```
