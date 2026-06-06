# Awards Endpoint

The Awards endpoint provides access to individual research grants and funding awards —
the specific financial instruments through which funders support scholarly work.

**Endpoint path:** `awards`
**Client access:** Not yet available as a dedicated resource client. Awards are accessible via works (`work.grants`, `work.awards`) and funders.

```python
from syntheca import SynthecaSession
from syntheca.endpoints import WorksFilters

async with SynthecaSession() as session:
    # Access awards through works
    filters = WorksFilters(has_doi=True)
    async for work in session.works.iterate(filters=filters, per_page=50):
        for grant in work.grants:
            print(f"{grant.award_id} from {grant.funder_display_name}")
```

## Supported Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Get by ID | Not yet implemented | Fetch a single award by OpenAlex ID |
| Search | Not yet implemented | Search awards |
| Iterate | Not yet implemented | Cursor-based pagination over filtered results |

## AwardsFilters Field Reference

### Core Metadata Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `display_name` | `display_name` | `str` | Exact display name match |
| `funder` | `funder` | `str` | Funder OpenAlex ID |
| `funding_type` | `funding_type` | `str` | Type of funding (grant, contract, fellowship, etc.) |
| `funder_scheme` | `funder_scheme` | `str` | Funding scheme/program name |
| `doi` | `doi` | `str` | Award DOI |
| `funder_award_id` | `funder_award_id` | `str` | Funder's own award identifier |

### Date Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `from_publication_date` | `from_publication_date` | `str` | Lower bound date (inclusive) |
| `to_publication_date` | `to_publication_date` | `str` | Upper bound date (inclusive) |

### Financial Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `amount` | `amount` | `str` | Award amount (use range syntax) |
| `grant_income_by_currency` | `grant_income_by_currency` | `str` | Grant income in specific currency |

### People Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `lead_investigator_orcid` | `lead_investigator.orcid` | `str` | Lead investigator ORCID |
| `lead_investigator_family_name` | `lead_investigator.family_name` | `str` | Lead investigator family name |
| `lead_investigator_given_name` | `lead_investigator.given_name` | `str` | Lead investigator given name |

### Institution Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `institution_awarded_id` | `institution_awarded.id` | `str` | Institution OpenAlex ID |
| `institution_awarded_country_code` | `institution_awarded.country_code` | `str` | ISO country code |
| `institution_awarded_ror` | `institution_awarded.ror` | `str` | ROR ID |
| `institution_awarded_type` | `institution_awarded.type` | `str` | Institution type |
| `institution_awarded_continent` | `institution_awarded.continent` | `str` | Continent |

### Topic Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `primary_topic_id` | `primary_topic.id` | `str` | Primary topic OpenAlex ID |
| `topics_id` | `topics.id` | `str` | Any associated topic ID |

### Search Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `default_search` | `default.search` | `str` | Default search across multiple fields |

### Boolean & Presence Filters

| Field Name | Alias (OpenAlex) | Type | Description |
|-----------|-------------------|------|-------------|
| `has_funder` | `has_funder` | `bool` | Whether the award has a linked funder |

## Usage Examples

### Find awards for a specific funder

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    results = await session.funders.search(search="NIH", page_size=1)
    if results.results:
        funder = results.results[0]
        print(f"{funder.display_name}: {funder.awards_count} awards")

        # Discover awards through works
        from syntheca.endpoints import WorksFilters

        filters = WorksFilters(
            authorships_institutions_id="I31371856",
        )
        async for work in session.works.iterate(filters=filters, per_page=50):
            for grant in work.grants:
                if grant.funder_display_name:
                    print(f"  {grant.award_id} from {grant.funder_display_name}")
```

### Access award data from a work

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")

    for grant in work.grants:
        print(f"Funder: {grant.funder_display_name}")
        print(f"Award ID: {grant.award_id}")

    for award_id in work.awards:
        print(f"Award: {award_id}")
```

## Live API Notes

- The `institution_awarded` field is always a list (even when empty `[]`), not a single dict despite the singular name. Each element has shape `{id, display_name, ror, country_code, type, lineage}`.
- The OpenAlex docs filter table lists ~23 filters, but the live API supports 38+ filter fields. Send `?filter=nonexistent:foo` to discover all valid filters from the error message.
- The `funded_outputs` field returns raw OpenAlex work ID strings, not structured objects.
- The Awards endpoint is not listed in the OpenAlex `llms.txt` quick reference.
