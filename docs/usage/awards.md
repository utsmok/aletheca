# Awards

The Awards endpoint represents individual research grants and funding awards — the specific financial instruments through which funders support scholarly work. Each award links to its funder, investigators, funded outputs (works), and award metadata like amount, dates, and topics.

!!! warning "Not yet available as a resource client"
    The `Award` model exists but there is no dedicated `session.awards` resource client yet. Awards currently appear as nested data on works (via the `grants` field) and on funders. The examples below show the intended API once the Awards client is implemented.

## Award Data on Works

Awards are currently accessible through works. Each work has a `grants` field and an `awards` field:

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
        async for work in session.works.iterate(filters=filters, per_page=50):
            for grant in work.grants:
                if grant.funder_display_name:
                    print(f"  {grant.award_id} from {grant.funder_display_name}")
```

## Notes

- OpenAlex IDs for awards start with `A` (e.g. `A123456`). Note this shares the `A` prefix with Authors — use context to distinguish.
- Not all funders have complete award data in OpenAlex; coverage varies by funder and country.
- The `funded_outputs` list contains OpenAlex work IDs, not full work objects — fetch works separately if you need full metadata.
- Award amounts may be in various currencies; check the `currency` field before comparing amounts.
- The `funding_type` field describes the instrument (grant, contract, fellowship, etc.).
- Use the Funders endpoint to explore funding organizations, then discover awards through works' `grants` field.
