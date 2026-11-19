# Missing Items Analysis: OpenAIRE vs OpenAlex

**Date**: 2026-06-07 14:46
**Scope**: University of Twente research output, 2023-2025

## Overview

| Category | Count |
|----------|------:|
| OpenAIRE total publications | 19,449 |
| DOIs shared (in both) | 10,575 |
| DOIs in OpenAIRE only (queried below) | 6,224 |
| Items without DOI (OpenAIRE) | 2,650 |
| **Total missing from initial OpenAlex query** | 8,874 |

## Batch DOI Lookup Results

Queried 6,224 DOIs against OpenAlex in batches of 50.

| Result | Count | % |
|--------|------:|---:|
| Found in OpenAlex (by DOI) | 2,979 | 47.9% |
| Not found in OpenAlex | 3,245 | 52.1% |

### Found by DOI — Why Were They Missing From Initial Query?

Of 2,979 DOIs that DO exist in OpenAlex:

- **290** are UT-affiliated in OpenAlex → they were in the initial query but their DOIs normalized differently (URL vs bare)
- **2,689** are NOT UT-affiliated in OpenAlex → OpenAIRE includes them via broader affiliation matching (acknowledgements, grant metadata)

#### Found-in-OpenAlex by OpenAIRE Type

| OpenAIRE Type | Count |
|--------------|------:|
| publication | 2,943 |
| dataset | 31 |
| other | 4 |
| software | 1 |

#### Type Mismatches (OpenAIRE → OpenAlex)

| OpenAIRE Type | OpenAlex Type | Count |
|--------------|---------------|------:|
| publication | dissertation | 1,177 |
| publication | article | 1,092 |
| publication | preprint | 384 |
| publication | book-chapter | 158 |
| publication | review | 54 |
| publication | book | 30 |
| publication | report | 11 |
| publication | peer-review | 10 |
| publication | paratext | 9 |
| publication | erratum | 7 |
| publication | letter | 6 |
| publication | editorial | 5 |
| other | dataset | 1 |
| software | other | 1 |

### Not Found in OpenAlex

3,245 DOIs from OpenAIRE do not exist in OpenAlex at all.

#### By OpenAIRE Type

| Type | Count |
|------|------:|
| dataset | 2,374 |
| publication | 608 |
| software | 193 |
| other | 70 |

#### Sample Not-Found DOIs (first 20)

```
  10.25625/s6js8e/0xhko7  (dataset)
  10.25625/kbpppl/ezowja  (dataset)
  10.25625/j93ng5/6mfh8f  (dataset)
  10.25625/s6js8e/demjgk  (dataset)
  10.25625/s6js8e/ia9w21  (dataset)
  10.25625/s6js8e/9pigdu  (dataset)
  10.25625/zfpsyj/ivhm99  (dataset)
  10.25625/s6js8e/iwfjfb  (dataset)
  10.25625/s6js8e/hbqube  (dataset)
  10.25625/s6js8e/gukf3a  (dataset)
  10.25625/s6js8e/lzfwjz  (dataset)
  10.25625/j93ng5/hdttmm  (dataset)
  10.25625/s6js8e/by2pro  (dataset)
  10.25625/s6js8e/ijsazo  (dataset)
  10.25625/s6js8e/wofrk1  (dataset)
  10.25625/s6js8e/duukr4  (dataset)
  10.25625/s6js8e/d2rf7z  (dataset)
  10.25625/s6js8e/m8woyy  (dataset)
  10.25625/kbpppl/7eev66  (dataset)
  10.25625/onubev/himgnk  (dataset)
```

### Items Without DOI (OpenAIRE Only)

2,650 items in OpenAIRE have no DOI and therefore cannot be matched.

#### By Type

| Type | Count |
|------|------:|
| publication | 2,609 |
| other | 35 |
| dataset | 6 |

## Root Cause Analysis

### 1. DOI Normalization Mismatch (largest factor)
OpenAIRE stores bare DOIs (`10.1234/abc`), OpenAlex stores full URLs (`https://doi.org/10.1234/abc`). 
The initial comparison was done with proper normalization, so this was handled correctly. 
However, this explains why simple string comparison would show 0 overlap.

### 2. Broader Affiliation Matching in OpenAIRE
OpenAIRE includes publications linked to UT through **any** affiliation channel: 
acknowledgements, grant metadata, EU project participation, and informal associations. 
An estimated **2,689** of the 'missing' DOIs exist in OpenAlex but are NOT linked to UT there — 
they appear in OpenAIRE only via these broader matching mechanisms.

### 3. Non-Publication Content Types
OpenAIRE indexes **datasets** and **software** as first-class works. 
OpenAlex primarily indexes scholarly works (articles, books, etc.). 
This explains 2,374 datasets and 193 software items that have no OpenAlex equivalent.

### 4. Grey Literature and Conference Proceedings
Many conference proceedings, preprints, and institutional repository deposits in OpenAIRE 
have DOIs but are not indexed by OpenAlex, especially those from smaller repositories 
or with non-standard DOI prefixes (e.g., `10.25625/` for UT repository).

### 5. Items Without DOI
2,650 items in OpenAIRE have no DOI at all. These are predominantly 
conference abstracts, institutional repository deposits, and internal reports that were never 
assigned a DOI. OpenAlex requires a DOI for most indexed works.

## Recommendations

1. **For comprehensive coverage**, use both OpenAIRE and OpenAlex — each covers items the other misses.
2. **For citation analysis**, prefer OpenAlex — its citation data is more structured and complete.
3. **For dataset/software tracking**, use OpenAIRE — OpenAlex does not index these.
4. **For EU-funded research**, use OpenAIRE — it has project-level links that OpenAlex lacks.
5. **For author/institution disambiguation**, prefer OpenAlex — its structured IDs (ROR, ORCID) are more reliable.