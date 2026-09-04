# Awards Endpoint

The Awards endpoint provides access to individual research grants and funding awards —
the specific financial instruments through which funders support scholarly work.

**Endpoint path:** `awards`
**Client access:** `session.awards` (via `AlethecaSession`)

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    # Fetch a single award
    award = await session.awards.get("G5066037109")
    print(f"{award.display_name}: {award.funder}")

    # Search awards
    results = await session.awards.search(search="cancer", per_page=10)
    for award in results.results:
        print(f"  {award.display_name} ({award.funding_type})")

    # Iterate with filters
    from aletheca.endpoints import AwardsFilters

    filters = AwardsFilters(funder_id="F4320306100")
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

Field names follow the live API's valid-filter list (the API enumerates it in
the 400 error returned for invalid fields). Filters that the API rejects —
`funder.country_code`, `lead_investigator.id`, `co_lead_investigator.id`, plain
`funder` and `display_name`, and `from_/to_*_date` ranges — are intentionally
not modelled.

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `doi` | `doi` | `str` | Award DOI |
| `funder_name` | `funder_name` | `str` | Funder display name |
| `funder_award_id` | `funder_award_id` | `str` | Funder's own award identifier |
| `funder_scheme` | `funder_scheme` | `str` | Funder's grant scheme |
| `funding_type` | `funding_type` | `str` | Kind of funding |
| `provenance` | `provenance` | `str` | Data source of the award |
| `currency` | `currency` | `str` | ISO 4217 currency code |
| `amount` | `amount` | `float` | Award amount |
| `start_year` / `end_year` | same | `int` | Award period years |
| `funded_outputs_count` | `funded_outputs_count` | `int` | Number of funded works |
| `funder_id` | `funder.id` | `str` | Funder OpenAlex ID |
| `funder_ror` | `funder.ror` | `str` | Funder ROR |
| `funder_doi` | `funder.doi` | `str` | Funder DOI |
| `lead_investigator_orcid` | `lead_investigator.orcid` | `str` | Lead investigator ORCID |
| `lead_investigator_given_name` | `lead_investigator.given_name` | `str` | Lead investigator given name |
| `lead_investigator_family_name` | `lead_investigator.family_name` | `str` | Lead investigator family name |
| `lead_investigator_affiliation_name` | `lead_investigator.affiliation.name` | `str` | Lead investigator affiliation |
| `lead_investigator_affiliation_country` | `lead_investigator.affiliation.country` | `str` | Lead investigator affiliation country |
| `institution_awarded_id` | `institution_awarded.id` | `str` | Institution OpenAlex ID |
| `institution_awarded_ror` | `institution_awarded.ror` | `str` | Institution ROR |
| `institution_awarded_country_code` | `institution_awarded.country_code` | `str` | Institution country code |
| `institution_awarded_type` | `institution_awarded.type` | `str` | Institution type |
| `institution_awarded_lineage` | `institution_awarded.lineage` | `str` | Institution lineage |
| `institution_awarded_continent` | `institution_awarded.continent` | `str` | Institution continent |
| `primary_topic_id` etc. | `primary_topic.{id,subfield.id,field.id,domain.id}` | `str` | Primary topic filters |
| `topics_id` etc. | `topics.{id,subfield.id,field.id,domain.id}` | `str` | Topic filters |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name_search` | `display_name.search` | `str` | Search within display name |
| `description_search` | `description.search` | `str` | Search within description |
| `text_search` | `text.search` | `str` | Full-text search |
| `default_search` | `default.search` | `str` | Default search across multiple fields |

## Usage Examples

### Find awards for a specific funder

```python
from aletheca import AlethecaSession
from aletheca.endpoints import AwardsFilters

async with AlethecaSession() as session:
    filters = AwardsFilters(funder_id="F4320306100")
    async for award in session.awards.iterate(filters=filters, per_page=50):
        print(f"{award.display_name}: {award.amount} {award.currency}")
```

### Search awards by keyword

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.awards.search(search="machine learning", per_page=10)
    print(f"Found {results.meta.count} awards")
    for award in results.results:
        print(f"  {award.display_name} ({award.funding_type})")
```

### Access award data from a work

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
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
