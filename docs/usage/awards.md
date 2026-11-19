# Awards

The Awards endpoint represents individual research grants and funding awards — the specific financial instruments through which funders support scholarly work. Each award links to its funder, investigators, funded outputs (works), and award metadata like amount, dates, and topics. Access it through `session.awards`.

## Quick Start

### Get an award by OpenAlex ID

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    award = await session.awards.get("G5066037109")
    print(f"{award.display_name}: {award.funder}")
```

### Search awards

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    results = await session.awards.search(search="machine learning", page_size=10)
    print(f"Found {results.meta.count} awards")
    for award in results.results:
        print(f"  {award.display_name} ({award.funding_type})")
```

## Award Data on Works

Each work carries award data in a `grants` field and an `awards` field:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")

    # Grant/funding info attached to the work
    for grant in work.grants:
        print(f"Funder: {grant.funder_display_name}")
        print(f"Award ID: {grant.award_id}")

    # Award IDs (OpenAlex IDs)
    for award_id in work.awards:
        print(f"Award: {award_id}")

    # Funder information
    for funder in work.funders:
        print(f"Funder: {funder.display_name}")
```

To fetch full award details for the IDs on a work:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")

    for award_id in work.awards:
        award = await session.awards.get(award_id.split("/")[-1])
        print(f"{award.display_name} from {award.funder}")
```

## Award Model Fields

The `Award` model includes the following fields (used when awards are returned from the API):

### Core Information

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | `str \| None` | Award title |
| `description` | `str \| None` | Award description |
| `doi` | `str \| None` | Award DOI |
| `funder_award_id` | `str \| None` | Funder's own award identifier |
| `funder` | `dict \| None` | Funder organization (dehydrated) |
| `funding_type` | `str \| None` | Type of funding (grant, contract, etc.) |
| `funder_scheme` | `str \| None` | Funding scheme/program name |

### Financial Details

| Field | Type | Description |
|-------|------|-------------|
| `amount` | `float \| None` | Award amount |
| `currency` | `str \| None` | Currency code |

### Duration

| Field | Type | Description |
|-------|------|-------------|
| `start_date` | `str \| None` | Award start date |
| `end_date` | `str \| None` | Award end date |
| `start_year` | `int \| None` | Award start year |
| `end_year` | `int \| None` | Award end year |

### People

| Field | Type | Description |
|-------|------|-------------|
| `lead_investigator` | `dict \| None` | Principal investigator |
| `co_lead_investigator` | `dict \| None` | Co-principal investigator |
| `investigators` | `list[dict]` | All investigators |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `institution_awarded` | `list[dict]` | Institutions receiving the award — always a list (even when empty), not a single dict |
| `funded_outputs` | `list[str]` | OpenAlex IDs of funded works |
| `funded_outputs_count` | `int \| None` | Number of funded works |
| `landing_page_url` | `str \| None` | Award landing page |

### Classification

| Field | Type | Description |
|-------|------|-------------|
| `primary_topic` | `DehydratedTopic \| None` | Primary topic classification |
| `topics` | `list[DehydratedTopic]` | All associated topics |

## Accessing Awards via Funders

You can discover awards through the funder relationship:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    # Find a funder
    results = await session.funders.search(search="NIH", page_size=1)
    if results.results:
        funder = results.results[0]
        print(f"{funder.display_name}: {funder.awards_count} awards")

        # Award IDs appear in work.grants and work.awards when filtering
        # works by funder
        from aletheca.endpoints import WorksFilters

        filters = WorksFilters(
            authorships_institutions_id="I31371856",
        )
        async for work in session.works.iterate(filters=filters, page_size=50):
            for grant in work.grants:
                if grant.funder_display_name:
                    print(f"  {grant.award_id} from {grant.funder_display_name}")
```

## Filtering

Use `AwardsFilters` to construct structured filter queries:

```python
from aletheca import AlethecaSession
from aletheca.endpoints import AwardsFilters

async with AlethecaSession() as session:
    filters = AwardsFilters(funder_id="F4320306100")
    async for award in session.awards.iterate(filters=filters, page_size=50):
        print(f"{award.display_name}: {award.amount} {award.currency}")
```

## Filter reference

Field names follow the live API's valid-filter list (the API enumerates it in
the 400 error returned for invalid fields). Filters that the API rejects —
`funder.country_code`, `lead_investigator.id`, `co_lead_investigator.id`, plain
`funder` and `display_name`, and `from_/to_*_date` ranges — are intentionally
not modelled.

### Core Metadata Filters

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

## Notes

- OpenAlex IDs for awards start with `A` (e.g. `A123456`). Note this shares the `A` prefix with Authors — use context to distinguish.
- Not all funders have complete award data in OpenAlex; coverage varies by funder and country.
- The `funded_outputs` list contains OpenAlex work IDs, not full work objects — fetch works separately if you need full metadata.
- Award amounts may be in various currencies; check the `currency` field before comparing amounts.
- The `funding_type` field describes the instrument (grant, contract, fellowship, etc.).
- Use the Funders endpoint to explore funding organizations, then discover awards through works' `grants` field.
- The OpenAlex docs filter table lists ~23 filters, but the live API supports 38+ filter fields. Send `?filter=nonexistent:foo` to discover all valid filters from the error message.
- The API returns more filters than are modeled here. Use `extra="allow"` to pass additional filters via keyword arguments.
