# Awards Endpoint

The Awards endpoint provides access to individual research grants and funding awards —
the specific financial instruments through which funders support scholarly work.

**Endpoint path:** `awards`
**Client access:** `session.awards` (via `SynthecaSession`)

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    # Fetch a single award
    award = await session.awards.get("A12345678")
    print(f"{award.display_name}: {award.funder}")

    # Search awards
    results = await session.awards.search(search="cancer", per_page=10)
    for award in results.results:
        print(f"  {award.display_name} ({award.funding_type})")

    # Iterate with filters
    from syntheca.endpoints import AwardsFilters

    filters = AwardsFilters(funder="F4320306100")
    async for award in session.awards.iterate(filters=filters, per_page=50):
        print(f"{award.display_name}: {award.amount} {award.currency}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | `session.awards.get(id)` | Fetch a single award by OpenAlex ID |
| Search | `session.awards.search(search=..., ...)` | Search awards by keyword |
| Iterate | `session.awards.iterate(filters=..., ...)` | Cursor-based pagination over filtered results |

## AwardsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `funder` | `funder` | `str` | Funder identifier |
| `funder_award_id` | `funder_award_id` | `str` | Funder's own award identifier |
| `funder_id` | `funder.id` | `str` | Funder OpenAlex ID |
| `funder_country_code` | `funder.country_code` | `str` | Funder ISO country code |
| `lead_investigator_id` | `lead_investigator.id` | `str` | Lead investigator ID |
| `co_lead_investigator_id` | `co_lead_investigator.id` | `str` | Co-lead investigator ID |
| `institution_awarded_id` | `institution_awarded.id` | `str` | Institution OpenAlex ID |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within display name |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

### Date Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `from_awarded_date` | `from_awarded_date` | `str` | Awarded date lower bound (inclusive) |
| `to_awarded_date` | `to_awarded_date` | `str` | Awarded date upper bound (inclusive) |
| `from_created_date` | `from_created_date` | `str` | Created date lower bound |
| `to_created_date` | `to_created_date` | `str` | Created date upper bound |
| `from_updated_date` | `from_updated_date` | `str` | Updated date lower bound |
| `to_updated_date` | `to_updated_date` | `str` | Updated date upper bound |

## Usage Examples

### Find awards for a specific funder

```python
from syntheca import SynthecaSession
from syntheca.endpoints import AwardsFilters

async with SynthecaSession() as session:
    filters = AwardsFilters(funder_id="F4320306100")
    async for award in session.awards.iterate(filters=filters, per_page=50):
        print(f"{award.display_name}: {award.amount} {award.currency}")
```

### Search awards by keyword

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    results = await session.awards.search(search="machine learning", per_page=10)
    print(f"Found {results.meta.count} awards")
    for award in results.results:
        print(f"  {award.display_name} ({award.funding_type})")
```

### Access award data from a work

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")

    for award_id in work.awards:
        # Fetch full award details
        award = await session.awards.get(award_id.split("/")[-1])
        print(f"{award.display_name} from {award.funder}")
```

## Live API Notes

- The `institution_awarded` field is always a list (even when empty `[]`), not a single dict despite the singular name. Each element has shape `{id, display_name, ror, country_code, type, lineage}`.
- The OpenAlex docs filter table lists ~23 filters, but the live API supports 38+ filter fields. Send `?filter=nonexistent:foo` to discover all valid filters from the error message.
- The `funded_outputs` field returns raw OpenAlex work ID strings, not structured objects.
- The Awards endpoint is not listed in the OpenAlex `llms.txt` quick reference.
- The OpenAlex API returns more filters than are modeled here. Use `extra="allow"` to pass additional filters via keyword arguments.
