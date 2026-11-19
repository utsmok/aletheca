# OpenAIRE vs OpenAlex: University of Twente Research Output Comparison (2023-2025)

Analysis date: 2026-06-07
Scope: All publications affiliated with the University of Twente, published 2023-01-01 to 2025-12-31.

## Summary

| Metric | OpenAIRE (AIREloom) | OpenAlex (Aletheca) | Difference |
|--------|-------------------:|--------------------:|-----------:|
| **Total publications** | 19,449 | 11,982 | OpenAIRE +62% |
| **Open Access** | 14,534 (74.7%) | 10,788 (90.0%) | OpenAlex OA rate +15pp |
| **Publications with citations** | 7,299 (37.5%) | 7,714 (64.4%) | OpenAlex +27pp |
| **Mean citations** | — | 9.6 | — |
| **Median citations** | — | 4.0 | — |
| **Max citations** | — | 621 | — |
| **DOI coverage** | 16,799 (86.5%) | ~11,982 (~100%) | OpenAlex near-universal DOI |
| **Projects** | 681 | N/A | OpenAlex has no project entity |
| **Scholix links** | 64,381 | N/A | OpenAlex has no Scholix equivalent |
| **Runtime** | ~14 min | ~2 min | OpenAlex ~7x faster |

## Publication Counts by Year

| Year | OpenAIRE | OpenAlex |
|------|---------:|---------:|
| 2023 | 7,060 | 4,065 |
| 2024 | 5,906 | 3,885 |
| 2025 | 6,483 | 4,032 |

OpenAIRE consistently shows ~65-75% more publications per year.

## Publication Type Distribution

| Type | OpenAIRE | OpenAlex |
|------|--------:|---------:|
| Article | 9,656 | 8,980 |
| Preprint | — | 1,143 |
| Book Chapter | 2,304 | 807 |
| Review | — | 381 |
| Dataset | — | 210 |
| Other/Conference | 7,489 | varies |
| Book | — | 48 |

OpenAIRE groups many items as "Other" and has significantly more conference proceedings and book chapters. OpenAlex has explicit preprint, dataset, and peer-review categories that OpenAIRE lacks.

## Top Authors

| Author | OpenAIRE Pubs | OpenAlex Pubs |
|--------|--------------:|--------------:|
| Sabine Siesling | ~100 | 108 |
| Luigi Lombardo | — | 103 |
| Alfred Stein | — | 86 |
| Riemer Slart | — | 87 |

The top authors appear in both databases, though OpenAIRE's author disambiguation is less reliable.

## Open Access Comparison

| OA Status | OpenAIRE | OpenAlex |
|-----------|---------:|---------:|
| Open (total) | 14,534 (74.7%) | 10,788 (90.0%) |
| Gold | — | 2,864 |
| Green | — | 3,754 |
| Hybrid | — | 3,109 |
| Diamond | — | 663 |
| Bronze | — | 398 |
| Closed | — | 1,194 |

OpenAlex reports a 90% OA rate vs OpenAIRE's 74.7%. This discrepancy likely stems from different OA classification methods — OpenAlex counts items available in any repository (including preprint servers), while OpenAIRE applies stricter publisher-version criteria.

## Top Publishers

| Publisher | OpenAlex Pubs |
|-----------|--------------:|
| Elsevier BV | 2,165 |
| Springer Nature | 1,021 |
| Wiley | 565 |
| MDPI | 487 |
| IEEE | 307 |
| ACS | 267 |
| Nature Portfolio | 224 |

## Country Collaboration (OpenAlex)

| Country | Publications |
|---------|-------------:|
| NL | 39,768 |
| DE | 5,309 |
| US | 4,707 |
| CN | 3,200 |
| GB | 2,911 |
| IT | 2,568 |

Note: OpenAlex country counts include multi-author co-authorship, so totals exceed the publication count (each publication counted once per unique country among its authors).

## Top Funders (OpenAlex)

| Funder | Publications |
|--------|-------------:|
| NWO | 1,395 |
| European Commission | 997 |
| University of Twente | 704 |
| NSFC (China) | 395 |
| DFG (Germany) | 312 |

## Key Differences

### Coverage
- **OpenAIRE covers significantly more items** (19,449 vs 11,982). The difference is likely due to:
  - OpenAIRE includes more conference proceedings and grey literature
  - OpenAIRE has broader institutional affiliation matching (includes informal affiliations in acknowledgements)
  - OpenAlex relies on structured author-institution links, which may miss some affiliations

### Data Quality
- **OpenAlex has richer structured metadata**: explicit author positions, institutional IDs (ROR), topic taxonomy, OA status classification, funder IDs
- **OpenAIRE has Scholix integration**: links between publications and datasets/software, unavailable in OpenAlex
- **OpenAIRE has project-level data**: 681 EU-funded projects with funding details

### Performance
- **OpenAlex API is significantly faster**: ~2 min vs ~14 min, due to:
  - Cursor pagination with 200-item pages (OpenAIRE: 100-item pages)
  - No Scholix queries needed (OpenAlex has native citation data)
  - Higher rate limits

### Classification
- **OpenAlex has finer type granularity**: 15 distinct types including preprint, dataset, peer-review, paratext
- **OpenAIRE lumps many items as "Other"**: ~5,300 items classified generically

## Bugs Fixed During Porting

### 1. `AlethecaResourceClient.count()` returned 0 (aletheca)
**Cause**: `BaseResourceClient.count()` in bibliofabric reads `response.header.numFound` (OpenAIRE format), but OpenAlex returns `response.meta.count`.
**Fix**: Override `count()` in `AlethecaResourceClient` to read `meta.count` from OpenAlex response envelope.

### 2. `OpenAccess.any_repository_has_fulltext: bool = False` rejected `None` (aletheca)
**Cause**: OpenAlex API sends `null` for this field on many works, but the Pydantic model required `bool`.
**Fix**: Changed to `bool | None = None`.

### 3. `Location.is_oa: bool = False` rejected `None` (aletheca)
**Cause**: Same issue — API sends `null` for `is_oa` on some locations.
**Fix**: Changed to `bool | None = None`.

## Files Changed

| File | Change |
|------|--------|
| `aletheca/examples/comprehensive_analysis.py` | New — ported analysis script |
| `aletheca/src/aletheca/resources/_standard.py` | Added `count()` override for `meta.count` |
| `aletheca/src/aletheca/models/common.py` | Fixed `any_repository_has_fulltext` and `is_oa` nullable |
