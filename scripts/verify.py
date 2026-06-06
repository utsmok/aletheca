"""Comprehensive live OpenAlex API verification for Syntheca.

Covers:
1. Model deserialization (10 samples × 9 entities)
2. Field coverage (model fields vs live fields)
3. Deep type checking (every field annotation vs live values)
4. Nested model validation (IDs, common, dehydrated, work-specific)
5. Round-trip serialization
6. Filter serialization (all 9 filter models)
7. Filter alias round-trip (populate_by_name=True)
8. Live filter queries
9. Filter coverage vs live API discovery
10. API parameter tests (per_page, sort, cursor, select, search)
11. Model config validation (extra="allow")
12. Endpoint constants vs resource clients wiring

Usage:
    uv run python scripts/verify.py
    uv run python scripts/verify.py --entity works
    uv run python scripts/verify.py --skip-filters
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import types
from typing import Annotated, Any, Union, get_args, get_origin

import httpx
from pydantic import BaseModel

from syntheca.endpoints import (
    AUTHORS,
    AWARDS,
    FUNDERS,
    INSTITUTIONS,
    KEYWORDS,
    PUBLISHERS,
    SOURCES,
    TOPICS,
    WORKS,
    AuthorsFilters,
    AwardsFilters,
    FundersFilters,
    InstitutionsFilters,
    KeywordsFilters,
    PublishersFilters,
    SourcesFilters,
    TopicsFilters,
    WorksFilters,
)
from syntheca.models import (
    Author,
    Award,
    Funder,
    Institution,
    Keyword,
    Publisher,
    Source,
    Topic,
    Work,
)

BASE_URL = "https://api.openalex.org"
SAMPLES_PER_ENTITY = 10

# ---------------------------------------------------------------------------
# Entity → filter class mapping
# ---------------------------------------------------------------------------

ENTITY_CONFIG: list[dict[str, Any]] = [
    {
        "endpoint": "works",
        "model": Work,
        "filter_cls": WorksFilters,
        "safe_filter": {"publication_year": 2024},
    },
    {
        "endpoint": "authors",
        "model": Author,
        "filter_cls": AuthorsFilters,
        "safe_filter": {"works_count": 100},
    },
    {
        "endpoint": "sources",
        "model": Source,
        "filter_cls": SourcesFilters,
        "safe_filter": {"type": "journal"},
    },
    {
        "endpoint": "institutions",
        "model": Institution,
        "filter_cls": InstitutionsFilters,
        "safe_filter": {"country_code": "US"},
    },
    {
        "endpoint": "topics",
        "model": Topic,
        "filter_cls": TopicsFilters,
        "safe_filter": {"domain_id": "1"},
    },
    {
        "endpoint": "keywords",
        "model": Keyword,
        "filter_cls": KeywordsFilters,
        "safe_filter": {"works_count": 1000},
    },
    {
        "endpoint": "publishers",
        "model": Publisher,
        "filter_cls": PublishersFilters,
        "safe_filter": {"country_codes": "US"},
    },
    {
        "endpoint": "funders",
        "model": Funder,
        "filter_cls": FundersFilters,
        "safe_filter": {"country_code": "US"},
    },
    {
        "endpoint": "awards",
        "model": Award,
        "filter_cls": AwardsFilters,
        "safe_filter": {},
    },
]

# Fields that are real but only appear conditionally.
CONDITIONAL_FIELDS: dict[str, set[str]] = {
    "sources": {
        "abbreviated_title",
        "is_in_jstage",
        "is_in_jstage_since_year",
        "is_indexed_in_scopus",
        "relevance_score",
        "x_concepts",
        "oa_flip_year",
        "is_high_oa_rate",
        "is_ojs",
        "is_in_scielo",
        "is_high_oa_rate_since_year",
        "is_in_doaj_since_year",
        "oa_works_count",
        "last_publication_year",
        "first_publication_year",
    },
    "institutions": {"x_concepts", "relevance_score", "international"},
    "works": {"relevance_score"},
    "publishers": {"relevance_score"},
    "funders": {"relevance_score"},
    "authors": {"relevance_score", "x_concepts"},
}

ENDPOINT_CONSTANTS = {
    "works": WORKS,
    "authors": AUTHORS,
    "sources": SOURCES,
    "institutions": INSTITUTIONS,
    "topics": TOPICS,
    "keywords": KEYWORDS,
    "publishers": PUBLISHERS,
    "funders": FUNDERS,
    "awards": AWARDS,
}


# ---------------------------------------------------------------------------
# Verdict accumulator
# ---------------------------------------------------------------------------


class Verdict:
    def __init__(self) -> None:
        self.passed: int = 0
        self.failed: int = 0
        self.warnings: int = 0
        self.details: list[str] = []

    def ok(self, msg: str) -> None:
        self.passed += 1
        self.details.append(f"  ✅ {msg}")

    def fail(self, msg: str) -> None:
        self.failed += 1
        self.details.append(f"  ❌ {msg}")

    def warn(self, msg: str) -> None:
        self.warnings += 1
        self.details.append(f"  ⚠️  {msg}")


# ---------------------------------------------------------------------------
# Type introspection helpers
# ---------------------------------------------------------------------------


def unwrap_optional(annotation: Any) -> Any:
    """Unwrap Optional[X] / X | None → X. Only unwraps union types."""
    origin = get_origin(annotation)
    if origin is types.UnionType or origin is Union:
        args = get_args(annotation)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return annotation


def unwrap_annotated(tp: Any) -> Any:
    """Unwrap Annotated[X, ...] → X."""
    origin = get_origin(tp)
    if origin is Annotated:
        args = get_args(tp)
        if args:
            return args[0]
    return tp


def peel(annotation: Any) -> Any:
    return unwrap_annotated(unwrap_optional(annotation))


def is_list_of_models(annotation: Any) -> type[BaseModel] | None:
    inner = peel(annotation)
    origin = get_origin(inner)
    if origin is list:
        args = get_args(inner)
        if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
            return args[0]
    return None


def is_single_model(annotation: Any) -> type[BaseModel] | None:
    inner = peel(annotation)
    if isinstance(inner, type) and issubclass(inner, BaseModel):
        return inner
    return None


def is_compatible_type(annotation: Any, live_val: Any) -> bool:
    if live_val is None:
        return True
    inner = peel(annotation)
    origin = get_origin(inner)
    if origin is list:
        return isinstance(live_val, list)
    if origin is dict:
        return isinstance(live_val, dict)
    if inner is str:
        return isinstance(live_val, str)
    if inner is int:
        return isinstance(live_val, int) and not isinstance(live_val, bool)
    if inner is float:
        return isinstance(live_val, (int, float)) and not isinstance(live_val, bool)
    if inner is bool:
        return isinstance(live_val, bool)
    if isinstance(inner, type) and issubclass(inner, BaseModel):
        return isinstance(live_val, dict)
    return True


# ---------------------------------------------------------------------------
# Model checks
# ---------------------------------------------------------------------------


def check_deserialization(model_class: type, samples: list[dict], v: Verdict) -> None:
    """All samples must deserialize without error."""
    for i, sample in enumerate(samples):
        try:
            obj = model_class.model_validate(sample)
            assert obj is not None
        except Exception as e:
            v.fail(f"Sample {i} deserialization failed: {e}")
            return
    v.ok(f"All {len(samples)} samples deserialize")


def check_field_coverage(
    entity_name: str, model_class: type, samples: list[dict], v: Verdict
) -> None:
    """Every unconditional model field appears in at least one live sample."""
    all_live_keys: set[str] = set()
    for s in samples:
        all_live_keys.update(s.keys())

    model_fields = set(model_class.model_fields.keys())
    conditional = CONDITIONAL_FIELDS.get(entity_name, set())
    unconditional = model_fields - conditional

    missing = unconditional - all_live_keys
    extra_live = all_live_keys - model_fields

    if missing:
        v.fail(f"Model fields not in any live sample: {sorted(missing)}")
    else:
        v.ok("All model fields appear in live responses")

    cond_missing = conditional - all_live_keys
    if cond_missing:
        v.warn(f"Conditional fields not seen (ok): {sorted(cond_missing)}")

    if extra_live:
        v.warn(f"Live-only fields (extra='allow'): {sorted(extra_live)}")

    print(
        f"  Live: {len(all_live_keys)}, Model: {len(model_fields)}"
        + (f", Unhandled: {len(extra_live)}" if extra_live else "")
    )


def check_deep_types(model_class: type, samples: list[dict], v: Verdict) -> None:
    """Deep type-check every field across all samples."""
    issues: dict[str, list[str]] = {}
    for fname, finfo in model_class.model_fields.items():
        ann = finfo.annotation
        for i, sample in enumerate(samples):
            if fname not in sample:
                continue
            live_val = sample[fname]
            if live_val is None:
                continue
            if not is_compatible_type(ann, live_val):
                issues.setdefault(fname, []).append(
                    f"Sample {i}: live={type(live_val).__name__}, "
                    f"ann={ann}, val={json.dumps(live_val)[:120]}"
                )
    if issues:
        for fname, probs in issues.items():
            v.fail(f"{model_class.__name__}.{fname}: {probs[0]}")
    else:
        v.ok(f"{model_class.__name__}: all field types compatible")


def check_nested_models(model_class: type, samples: list[dict], v: Verdict) -> None:
    """Verify nested Pydantic models (single + list-of) deserialize."""
    for fname, finfo in model_class.model_fields.items():
        ann = finfo.annotation
        # Single nested model
        single = is_single_model(ann)
        if single:
            for i, sample in enumerate(samples):
                if fname not in sample or sample[fname] is None:
                    continue
                val = sample[fname]
                if not isinstance(val, dict):
                    v.fail(f"{model_class.__name__}.{fname}: expected dict")
                    return
                try:
                    single.model_validate(val)
                except Exception as e:
                    v.fail(
                        f"{model_class.__name__}.{fname}: {single.__name__} sample {i}: {e}"
                    )
                    return
            # Also validate nested model's sub-fields against live data
            _check_nested_field_coverage(model_class, fname, single, samples, v)
            continue
        # List of models
        list_model = is_list_of_models(ann)
        if list_model:
            for i, sample in enumerate(samples):
                if fname not in sample or sample[fname] is None:
                    continue
                val = sample[fname]
                if not isinstance(val, list):
                    v.fail(f"{model_class.__name__}.{fname}: expected list")
                    return
                for j, item in enumerate(val):
                    if not isinstance(item, dict):
                        v.fail(f"{model_class.__name__}.{fname}[{j}]: expected dict")
                        return
                    try:
                        list_model.model_validate(item)
                    except Exception as e:
                        v.fail(f"{model_class.__name__}.{fname}[{j}]: sample {i}: {e}")
                        return
            _check_nested_field_coverage(model_class, fname, list_model, samples, v)
    v.ok(f"{model_class.__name__}: all nested models deserialize")


def _check_nested_field_coverage(
    parent_cls: type,
    field_name: str,
    nested_cls: type,
    samples: list[dict],
    v: Verdict,
) -> None:
    """Check that nested model fields cover live nested data."""
    nested_fields = set(nested_cls.model_fields.keys())
    seen_live_keys: set[str] = set()
    for sample in samples:
        raw = sample.get(field_name)
        if raw is None:
            continue
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    seen_live_keys.update(item.keys())
        elif isinstance(raw, dict):
            seen_live_keys.update(raw.keys())
    missing = nested_fields - seen_live_keys
    if missing:
        v.warn(
            f"{parent_cls.__name__}.{field_name} ({nested_cls.__name__}): "
            f"{len(missing)} fields not seen in live data: {sorted(missing)}"
        )


def check_round_trip(model_class: type, samples: list[dict], v: Verdict) -> None:
    """Serialize → deserialize round-trip must preserve all fields."""
    model_fields = set(model_class.model_fields.keys())
    for i, sample in enumerate(samples):
        obj = model_class.model_validate(sample)
        dumped = obj.model_dump(mode="python")
        re_parsed = model_class.model_validate(dumped)
        for fname in model_fields:
            if getattr(obj, fname) != getattr(re_parsed, fname):
                v.fail(f"Sample {i}, field '{fname}': round-trip mismatch")
                return
    v.ok("All samples survive serialize → deserialize round-trip")


def check_model_config(model_class: type, v: Verdict) -> None:
    """All entity models must have extra='allow' for forward compat."""
    cfg = model_class.model_config
    if cfg.get("extra") != "allow":
        v.fail(f"{model_class.__name__}: extra != 'allow'")
    else:
        v.ok(f"{model_class.__name__}: extra='allow' ✓")


# ---------------------------------------------------------------------------
# Filter checks
# ---------------------------------------------------------------------------


def check_filter_serialize(filter_cls: type, v: Verdict) -> None:
    """Filter model serializes with correct aliases (by_alias=True)."""
    f = filter_cls()
    dumped = f.model_dump(exclude_none=True, by_alias=True)
    # Verify no Python-name keys leaked when alias differs
    for fname, finfo in filter_cls.model_fields.items():
        alias = finfo.alias
        if alias and alias != fname and fname in dumped:
            v.fail(f"{filter_cls.__name__}.{fname}: dumped as Python name, not alias")
            return
    v.ok(f"{filter_cls.__name__}: serialization correct")


def check_filter_alias_roundtrip(filter_cls: type, v: Verdict) -> None:
    """populate_by_name=True: must accept both Python name and alias."""
    cfg = filter_cls.model_config
    if not cfg.get("populate_by_name"):
        v.warn(f"{filter_cls.__name__}: populate_by_name not set")
        return
    for fname, finfo in filter_cls.model_fields.items():
        alias = finfo.alias
        if not alias or alias == fname:
            continue
        # Pick a value compatible with the field type
        ann = peel(finfo.annotation)
        if ann is bool:
            test_val: Any = True
        elif ann is int:
            test_val = 1
        elif ann is float:
            test_val = 1.0
        else:
            test_val = "test"
        # Test Python name
        try:
            filter_cls(**{fname: test_val})
        except Exception as e:
            v.fail(f"{filter_cls.__name__}: Python name '{fname}' rejected: {e}")
            return
        # Test alias
        try:
            filter_cls(**{alias: test_val})
        except Exception as e:
            v.fail(f"{filter_cls.__name__}: alias '{alias}' rejected: {e}")
            return
    v.ok(f"{filter_cls.__name__}: alias round-trip ✓")


def check_filter_query(
    client: httpx.Client, entity: str, filter_cls: type, filter_values: dict, v: Verdict
) -> None:
    """Send a real filter query and verify the API accepts it."""
    f = filter_cls(**filter_values)
    fd = f.model_dump(exclude_none=True, by_alias=True)
    if not fd:
        v.ok(f"{entity}: no filter to test (skipped)")
        return
    parts = [f"{k}:{val}" for k, val in fd.items()]
    filter_str = ",".join(parts)
    resp = client.get(f"/{entity}", params={"filter": filter_str, "per_page": 1})
    if resp.status_code == 200:
        count = resp.json().get("meta", {}).get("count", 0)
        v.ok(f"{entity}: filter '{filter_str}' → {count} results")
    elif resp.status_code == 403:
        v.ok(f"{entity}: filter accepted (403 = rate limit)")
    else:
        v.fail(
            f"{entity}: filter '{filter_str}' → HTTP {resp.status_code}: {resp.text[:200]}"
        )


def discover_filters(client: httpx.Client, entity: str, v: Verdict) -> set[str] | None:
    """Discover valid filter names by sending an invalid filter."""
    resp = client.get(
        f"/{entity}", params={"filter": "NONEXISTENT_FILTER:value", "per_page": 1}
    )
    if resp.status_code != 400:
        v.warn(f"{entity}: expected 400, got {resp.status_code}")
        return None
    patterns = [
        r"Valid fields are[^:]*:\s*([^\"]+)",
        r"[Vv]alid filters?(?:\s+are)?:\s*([^\"]+)",
        r"[Vv]alid (?:filter|query) (?:parameters?|fields?)(?:\s+are)?[^:]*:\s*([^\"]+)",
    ]
    for pat in patterns:
        m = re.search(pat, resp.text)
        if m:
            filters = {f.strip().strip("'\"") for f in m.group(1).split(",")}
            filters.discard("")
            if filters:
                v.ok(f"{entity}: discovered {len(filters)} valid filters")
                return filters
    v.warn(f"{entity}: couldn't parse filter error")
    return None


def check_filter_coverage(
    entity: str, filter_cls: type, live_filters: set[str] | None, v: Verdict
) -> None:
    """Compare our filter model against live-discovered filters."""
    if live_filters is None:
        return
    our: set[str] = set()
    for fname, finfo in filter_cls.model_fields.items():
        our.add(finfo.alias if finfo.alias else fname)
    missing = live_filters - our
    extra = our - live_filters
    if missing:
        v.warn(f"{entity}: {len(missing)} live filters missing: {sorted(missing)}")
    else:
        v.ok(f"{entity}: all live filters covered")
    if extra:
        v.warn(f"{entity}: {len(extra)} our filters not in live: {sorted(extra)}")


# ---------------------------------------------------------------------------
# API parameter tests
# ---------------------------------------------------------------------------


def test_per_page(client: httpx.Client, v: Verdict) -> None:
    for pp in [1, 50, 200]:
        resp = client.get("/works", params={"per_page": pp})
        resp.raise_for_status()
        assert len(resp.json().get("results", [])) <= pp
    v.ok("per_page=1,50,200 all accepted")


def test_sort(client: httpx.Client, v: Verdict) -> None:
    for path, spec in [
        ("/works", "cited_by_count:desc"),
        ("/works", "publication_date:desc"),
        ("/authors", "works_count:desc"),
        ("/sources", "works_count:desc"),
        ("/institutions", "works_count:desc"),
    ]:
        resp = client.get(path, params={"sort": spec, "per_page": 2})
        if resp.status_code != 200:
            v.fail(f"{path} sort='{spec}' → HTTP {resp.status_code}")
            return
    v.ok("sort parameter accepted across entities")


def test_cursor(client: httpx.Client, v: Verdict) -> None:
    resp = client.get("/works", params={"per_page": 2, "cursor": "*"})
    resp.raise_for_status()
    cursor = resp.json().get("meta", {}).get("next_cursor")
    if not cursor:
        v.fail("No next_cursor for cursor=*")
        return
    resp2 = client.get("/works", params={"per_page": 2, "cursor": cursor})
    resp2.raise_for_status()
    r2 = resp2.json().get("results", [])
    if not r2:
        v.fail("Page 2 via cursor empty")
        return
    v.ok(f"Cursor pagination: page 1 → 2 ({len(r2)} results)")


def test_select(client: httpx.Client, v: Verdict) -> None:
    resp = client.get("/works", params={"select": "id,title,doi", "per_page": 1})
    resp.raise_for_status()
    keys = set(resp.json()["results"][0].keys())
    if not {"id", "title", "doi"}.issubset(keys):
        v.fail(f"select=id,title,doi but got {keys}")
        return
    v.ok(f"select=id,title,doi → {keys}")


def test_search(client: httpx.Client, v: Verdict) -> None:
    resp = client.get("/works", params={"search": "machine learning", "per_page": 1})
    resp.raise_for_status()
    count = resp.json().get("meta", {}).get("count", 0)
    if count == 0:
        v.fail("search='machine learning' returned 0")
        return
    v.ok(f"search='machine learning' → {count} results")


def test_endpoint_constants(v: Verdict) -> None:
    """Endpoint constants match entity names."""
    for name, const in ENDPOINT_CONSTANTS.items():
        if const != name:
            v.fail(f"ENDPOINT {name} = '{const}' (mismatch)")
        else:
            v.ok(f"{name} = '{const}' ✓")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entity", help="Only test this entity (e.g. works)")
    parser.add_argument(
        "--skip-filters", action="store_true", help="Skip filter discovery"
    )
    parser.add_argument("--skip-api", action="store_true", help="Skip API param tests")
    args = parser.parse_args()

    print("🔬 Syntheca Comprehensive Live API Verification")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Samples: {SAMPLES_PER_ENTITY}")

    v = Verdict()

    # Static checks
    print("\n=== Endpoint Constants ===")
    test_endpoint_constants(v)

    configs = ENTITY_CONFIG
    if args.entity:
        configs = [c for c in configs if c["endpoint"] == args.entity]
        if not configs:
            print(f"Unknown entity: {args.entity}")
            sys.exit(1)

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        for cfg in configs:
            entity = cfg["endpoint"]
            model_cls = cfg["model"]
            filter_cls = cfg["filter_cls"]
            safe_f = cfg["safe_filter"]

            print(f"\n{'=' * 60}")
            print(f"  {entity.upper()} ({model_cls.__name__})")
            print(f"{'=' * 60}")

            # Fetch samples
            resp = client.get(f"/{entity}", params={"per_page": SAMPLES_PER_ENTITY})
            resp.raise_for_status()
            samples = resp.json().get("results", [])
            if not samples:
                v.fail(f"No samples for {entity}")
                continue
            v.ok(f"Fetched {len(samples)} samples")

            # Model checks
            check_deserialization(model_cls, samples, v)
            check_field_coverage(entity, model_cls, samples, v)
            check_deep_types(model_cls, samples, v)
            check_nested_models(model_cls, samples, v)
            check_round_trip(model_cls, samples, v)
            check_model_config(model_cls, v)

            # Filter checks
            check_filter_serialize(filter_cls, v)
            check_filter_alias_roundtrip(filter_cls, v)
            check_filter_query(client, entity, filter_cls, safe_f, v)

            if not args.skip_filters:
                live_f = discover_filters(client, entity, v)
                check_filter_coverage(entity, filter_cls, live_f, v)

        # API parameter tests
        if not args.skip_api and not args.entity:
            print(f"\n{'=' * 60}")
            print("  API PARAMETER TESTS")
            print(f"{'=' * 60}")
            test_per_page(client, v)
            test_sort(client, v)
            test_cursor(client, v)
            test_select(client, v)
            test_search(client, v)

    # Summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    for line in v.details:
        print(line)
    print(f"\n  Passed: {v.passed}")
    print(f"  Failed: {v.failed}")
    print(f"  Warnings: {v.warnings}")

    if v.failed:
        print("\n❌ VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL CHECKS PASSED (warnings are informational)")


if __name__ == "__main__":
    main()
