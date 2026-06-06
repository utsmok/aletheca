# API Verification Guide

This guide explains how to verify that Syntheca's models still match the live OpenAlex API. This is critical because the OpenAlex OpenAPI spec is incomplete and stale — the live API is the ground truth.

## Why This Matters

The OpenAlex API has several known issues that make passive trust in the spec unreliable:

- **50+ fields** returned by the live API are missing from the OpenAPI spec schemas
- At least **3 fields** in the spec don't exist in the live API (`longest_name`, `parsed_longest_name` on Author, `content_url` on Work)
- **Field renames** happen silently (e.g., `grants_count` → `awards_count` on Funders)
- **Field removals** are undocumented (e.g., `fatcat` ID removed from Sources)
- The spec has **wrong types** (e.g., `content_url` is `string` in spec but live API returns `content_urls` as an object)
- Filter tables in docs are incomplete (e.g., Awards lists ~23 filters but the API supports 38+)
- `per_page` maximum is documented as 100 but actually accepts 200

See [OPENALEX_BUG_REPORT.md](https://github.com/utsmok/syntheca/blob/main/OPENALEX_BUG_REPORT.md) for the full list of verified discrepancies.

## Quick Verification Script

This script fetches one sample per entity and checks field names against model fields:

```python
"""Quick verification that Syntheca models match the live OpenAlex API.

Usage:
    uv run python scripts/verify_api.py
"""

import httpx
import json
import sys

from syntheca.models import (
    Work,
    Author,
    Source,
    Institution,
    Topic,
    Keyword,
    Publisher,
    Funder,
    Award,
)

ENTITIES = {
    "works": Work,
    "authors": Author,
    "sources": Source,
    "institutions": Institution,
    "topics": Topic,
    "keywords": Keyword,
    "publishers": Publisher,
    "funders": Funder,
    "awards": Award,
}

BASE_URL = "https://api.openalex.org"


def verify_entity(entity_name: str, model_class: type) -> dict:
    """Fetch one sample and compare live fields against model fields."""
    resp = httpx.get(f"{BASE_URL}/{entity_name}", params={"per_page": 1})
    resp.raise_for_status()
    data = resp.json()
    samples = data.get("results", [])
    if not samples:
        return {"entity": entity_name, "error": "no results returned"}

    sample = samples[0]
    live_fields = set(sample.keys())
    model_fields = set(model_class.model_fields.keys())

    # Check deserialization
    try:
        model_class.model_validate(sample)
        deser_ok = True
        deser_error = None
    except Exception as e:
        deser_ok = False
        deser_error = str(e)

    # Find gaps
    missing_from_model = live_fields - model_fields
    missing_from_api = model_fields - live_fields

    return {
        "entity": entity_name,
        "deserialization": "PASS" if deser_ok else f"FAIL: {deser_error}",
        "live_field_count": len(live_fields),
        "model_field_count": len(model_fields),
        "in_live_not_model": sorted(missing_from_model),
        "in_model_not_live": sorted(missing_from_api),
    }


def main():
    print("=== OpenAlex API Verification ===\n")
    all_ok = True

    for entity_name, model_class in ENTITIES.items():
        result = verify_entity(entity_name, model_class)
        print(f"--- {entity_name} ---")
        print(f"  Deserialization: {result.get('deserialization', 'N/A')}")

        if "error" in result:
            print(f"  Error: {result['error']}")
            continue

        print(f"  Live fields: {result['live_field_count']}")
        print(f"  Model fields: {result['model_field_count']}")

        if result["in_live_not_model"]:
            # These are handled by extra="allow" but should be noted
            print(f"  Live-only fields (extra='allow'): {result['in_live_not_model']}")

        if result["in_model_not_live"]:
            print(f"  Model-only fields (not in live): {result['in_model_not_live']}")
            all_ok = False

        print()

    if all_ok:
        print("All checks passed.")
    else:
        print("Some model fields are not present in live API responses.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Full Verification Procedure

### Step 1: Fetch samples

Fetch 10 samples per entity to ensure coverage of field variations:

```bash
curl -s "https://api.openalex.org/works?per_page=10" | python -m json.tool > /tmp/works_samples.json
curl -s "https://api.openalex.org/authors?per_page=10" | python -m json.tool > /tmp/authors_samples.json
curl -s "https://api.openalex.org/sources?per_page=10" | python -m json.tool > /tmp/sources_samples.json
curl -s "https://api.openalex.org/institutions?per_page=10" | python -m json.tool > /tmp/institutions_samples.json
curl -s "https://api.openalex.org/topics?per_page=10" | python -m json.tool > /tmp/topics_samples.json
curl -s "https://api.openalex.org/keywords?per_page=10" | python -m json.tool > /tmp/keywords_samples.json
curl -s "https://api.openalex.org/publishers?per_page=10" | python -m json.tool > /tmp/publishers_samples.json
curl -s "https://api.openalex.org/funders?per_page=10" | python -m json.tool > /tmp/funders_samples.json
curl -s "https://api.openalex.org/awards?per_page=10" | python -m json.tool > /tmp/awards_samples.json
```

### Step 2: Deserialize each sample

For each entity, try deserializing every sample:

```python
import json
from syntheca.models import Work

with open("/tmp/works_samples.json") as f:
    data = json.load(f)

for i, sample in enumerate(data["results"]):
    try:
        work = Work.model_validate(sample)
        print(f"Sample {i}: OK")
    except Exception as e:
        print(f"Sample {i}: FAIL — {e}")
```

Deserialization must not raise on any sample. If it does, the model field types need updating.

### Step 3: Compare field sets

For each entity, compare the live response keys against the model's declared fields:

```python
from syntheca.models import Work

sample = data["results"][0]
live_fields = set(sample.keys())
model_fields = set(Work.model_fields.keys())

print("In live API but not in model:")
for f in sorted(live_fields - model_fields):
    print(f"  {f}: {type(sample[f]).__name__} = {repr(sample[f])[:80]}")

print("\nIn model but not in live API:")
for f in sorted(model_fields - live_fields):
    print(f"  {f}")
```

Fields in the live API but not in the model are handled by `extra="allow"` on all Syntheca models — they're preserved but not typed. If important fields are discovered, add them to the model explicitly.

Fields in the model but not in the live API indicate stale model fields that should be investigated.

### Step 4: Check live types match annotations

For each field present in both, verify the live type is compatible with the model annotation:

```python
from syntheca.models import Work

sample = data["results"][0]
model = Work.model_validate(sample)

for field_name, field_info in Work.model_fields.items():
    if field_name in sample:
        live_value = sample[field_name]
        live_type = type(live_value).__name__
        annotation = field_info.annotation
        print(f"  {field_name}: live={live_type}, annotation={annotation}")
```

Common mismatches to watch for:

- `null` vs expected `int` / `str` (should be `int | None` / `str | None`)
- `list` vs expected single `dict` (e.g., `institution_awarded` on Awards)
- `dict` vs expected `str` (e.g., `parent_publisher` on Publishers)
- `object` vs expected `str` (e.g., `content_urls` vs `content_url` on Works)

### Step 5: Discover valid filters

Send an invalid filter to discover all valid filter fields for an endpoint:

```bash
curl -s "https://api.openalex.org/awards?filter=nonexistent:foo&per_page=1"
```

The error message lists all valid filter names. Compare against the filter models in `syntheca.endpoints` and the docs in `docs/endpoints/`.

## Known Stale Areas

These are areas where the OpenAlex spec or docs are known to be stale (verified 2026-06-05):

| Area | Spec says | Live API says | Impact |
|------|-----------|---------------|--------|
| Works `content_url` | `string` field exists | `content_urls` as `object` with `pdf`, `grobid_xml` keys | Wrong name AND type |
| Works `works_api_url` | Listed in spec | Not returned | Stale field |
| Funders `grants_count` | Listed in spec | Returns `awards_count` instead | Stale name |
| Funders `works_api_url` | Listed in spec | Not returned | Stale field |
| Publishers `parent_publisher` | — | Object `{id, display_name}`, not string | Type differs |
| Awards `institution_awarded` | Not documented | Always a list, never a single dict | Wrong cardinality |
| Sources `fatcat` ID | — | No longer returned | Undocumented removal |
| Sources `is_in_jstage` | Not in spec | Returned by live API | Missing from spec |
| `per_page` max | 100 in `llms.txt` | Actually 200 | Wrong limit |
| Awards endpoint | Not in `llms.txt` | Exists with 14.7M records | Missing from docs |

## Automated Approach

### CI step

Add a scheduled verification test that runs weekly:

```yaml
# .github/workflows/verify-api.yml
name: Verify API Models
on:
  schedule:
    - cron: "0 6 * * 1"  # Weekly on Monday at 6 UTC
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run python scripts/verify_api.py
```

### pytest integration

Add a marks-based test suite for API verification:

```python
# tests/test_api_verification.py
import pytest
import httpx
from syntheca.models import Work, Author, Source, Institution, Topic, Keyword, Publisher, Funder, Award

@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url="https://api.openalex.org", timeout=30)

@pytest.mark.parametrize("entity_name,model_class", [
    ("works", Work),
    ("authors", Author),
    ("sources", Source),
    ("institutions", Institution),
    ("topics", Topic),
    ("keywords", Keyword),
    ("publishers", Publisher),
    ("funders", Funder),
    ("awards", Award),
])
def test_deserialization(client, entity_name, model_class):
    """Live API samples must deserialize without error."""
    resp = client.get(f"/{entity_name}", params={"per_page": 5})
    resp.raise_for_status()
    for sample in resp.json()["results"]:
        model_class.model_validate(sample)  # Must not raise

@pytest.mark.parametrize("entity_name,model_class", [
    ("works", Work),
    ("authors", Author),
    ("sources", Source),
    ("institutions", Institution),
    ("topics", Topic),
    ("keywords", Keyword),
    ("publishers", Publisher),
    ("funders", Funder),
    ("awards", Award),
])
def test_no_stale_model_fields(client, entity_name, model_class):
    """Model fields should all appear in live API responses."""
    resp = client.get(f"/{entity_name}", params={"per_page": 10})
    resp.raise_for_status()
    samples = resp.json()["results"]
    all_live_keys = set()
    for sample in samples:
        all_live_keys.update(sample.keys())

    model_fields = set(model_class.model_fields.keys())
    stale = model_fields - all_live_keys
    assert not stale, f"Model has fields not in live API: {stale}"
```

## Reference

For the complete list of verified OpenAlex API bugs, discrepancies, and suggestions, see:

- [OPENALEX_BUG_REPORT.md](https://github.com/utsmok/syntheca/blob/main/OPENALEX_BUG_REPORT.md) — Full bug report verified 2026-06-05
- [OpenAlex API docs](https://developers.openalex.org/)
- [OpenAlex OpenAPI spec](https://developers.openalex.org/api-reference/openapi.json)
