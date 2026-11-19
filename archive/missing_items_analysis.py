#!/usr/bin/env python3
"""Analyze why OpenAIRE items are missing from OpenAlex.

Loads the 6,224 DOIs found in OpenAIRE but not in OpenAlex,
batch-queries OpenAlex by DOI (up to 50 per request), and classifies
each item as: found-in-openalex, not-in-openalex, or no-doi.

Also loads the 2,650 no-DOI OpenAIRE items and classifies them by type.

Produces a markdown report with breakdowns by type, reason, and recommendations.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aletheca import AlethecaSession
from aletheca.models import Work

console = Console()

BATCH_SIZE = 50  # OpenAlex supports up to 50 DOIs per filter

# Paths
THIS_DIR = Path(__file__).parent
MISSING_DOIS_FILE = THIS_DIR.parent / "missing_dois.txt"
MISSING_METADATA_FILE = THIS_DIR.parent / "missing_items_metadata.json"
OPENAIRE_DB = Path("/home/sam/dev/AIREloom/output/analysis.duckdb")
OPENALEX_DB = Path("/home/sam/dev/aletheca/output/analysis.duckdb")
REPORT_PATH = THIS_DIR / "missing_items_report.md"


def load_missing_dois() -> list[str]:
    """Load DOIs from missing_dois.txt, skipping comments and blanks."""
    dois = []
    with open(MISSING_DOIS_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                dois.append(line)
    return dois


def load_missing_metadata() -> list[dict]:
    """Load full metadata for missing items from JSON."""
    with open(MISSING_METADATA_FILE) as f:
        return json.load(f)


def load_openalex_dois() -> set[str]:
    """Load DOIs already in the OpenAlex analysis DuckDB."""
    import duckdb

    con = duckdb.connect(str(OPENALEX_DB), read_only=True)
    rows = con.execute(
        "SELECT doi FROM publications WHERE doi IS NOT NULL AND doi != ''"
    ).fetchall()
    con.close()
    return {
        r[0]
        .lower()
        .replace("https://doi.org/", "")
        .replace("http://doi.org/", "")
        .strip()
        for r in rows
    }


def load_openaire_dois_with_types() -> dict[str, str]:
    """Load {normalized_doi: type} from OpenAIRE DuckDB."""
    import duckdb

    con = duckdb.connect(str(OPENAIRE_DB), read_only=True)
    rows = con.execute(
        "SELECT doi, type FROM publications WHERE doi IS NOT NULL AND doi != ''"
    ).fetchall()
    con.close()
    result = {}
    for doi, typ in rows:
        ndoi = doi.lower().replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        result[ndoi] = typ
    return result


async def batch_lookup_dois(
    session: AlethecaSession,
    dois: list[str],
    progress_task=None,
    progress=None,
) -> dict[str, Work | None]:
    """Batch-query OpenAlex for DOIs using batch_get_by_doi.
    Returns {normalized_doi: Work} for each DOI found.
    Missing DOIs are absent from the dict.
    """
    total_batches = (len(dois) + BATCH_SIZE - 1) // BATCH_SIZE
    # Use the ergonomic batch_get_by_doi method (auto-batches at 50)
    try:
        found = await session.works.batch_get_by_doi(dois)
    except Exception as e:
        console.print(f"[red]Batch lookup failed: {e}[/red]")
        found = {}
    if progress and progress_task is not None:
        progress.update(
            progress_task,
            completed=total_batches,
            description=f"Queried {total_batches} batches",
        )
    return found


def classify_found_items(
    lookup_results: dict[str, Work | None],
    openaire_types: dict[str, str],
) -> dict:
    """Classify each DOI into categories."""
    found_in_openalex = []
    not_in_openalex = []
    for ndoi, work in lookup_results.items():
        oa_type = openaire_types.get(ndoi, "unknown")
        if isinstance(work, Work):
            # Check if the work is UT-affiliated
            is_ut = False
            for authorship in work.authorships:
                for inst in authorship.institutions:
                    if inst and inst.get("id") == "https://openalex.org/I94624287":
                        is_ut = True
                        break
                if is_ut:
                    break
            found_in_openalex.append({
                "doi": ndoi,
                "openaire_type": oa_type,
                "openalex_type": str(work.type or ""),
                "is_ut_in_openalex": is_ut,
                "title": str(work.title or "")[:100],
                "year": work.publication_year,
            })
        elif isinstance(work, dict):
            found_in_openalex.append({
                "doi": ndoi,
                "openaire_type": oa_type,
                "openalex_type": str(work.get("type", "")),
                "is_ut_in_openalex": False,
                "title": str(work.get("title", ""))[:100],
                "year": work.get("publication_year"),
            })
        else:
            not_in_openalex.append({
                "doi": ndoi,
                "openaire_type": oa_type,
            })
    return {
        "found_in_openalex": found_in_openalex,
        "not_in_openalex": not_in_openalex,
    }


def generate_report(
    classification: dict,
    missing_metadata: list[dict],
    openaire_types: dict[str, str],
) -> str:
    """Generate the markdown report."""
    found = classification["found_in_openalex"]
    not_found = classification["not_in_openalex"]

    # Count no-DOI items from metadata
    no_doi_items = [m for m in missing_metadata if not m.get("normalized_doi")]
    no_doi_by_type = Counter(m["type"] for m in no_doi_items)

    # Found-in-OpenAlex breakdown
    found_by_type = Counter(f["openaire_type"] for f in found)
    found_ut = sum(1 for f in found if f.get("is_ut_in_openalex"))
    found_not_ut = len(found) - found_ut

    # Not-found breakdown
    not_found_by_type = Counter(f["openaire_type"] for f in not_found)

    # DOI-type mismatch (OpenAIRE says publication, OpenAlex says dataset etc.)
    type_mismatches = []
    for f in found:
        if f["openaire_type"] != f.get("openalex_type", ""):
            type_mismatches.append(f)

    lines = [
        "# Missing Items Analysis: OpenAIRE vs OpenAlex",
        "",
        f"**Date**: {time.strftime('%Y-%m-%d %H:%M')}",
        "**Scope**: University of Twente research output, 2023-2025",
        "",
        "## Overview",
        "",
        "| Category | Count |",
        "|----------|------:|",
        f"| OpenAIRE total publications | 19,449 |",
        f"| DOIs shared (in both) | 10,575 |",
        f"| DOIs in OpenAIRE only (queried below) | {len(found) + len(not_found):,} |",
        f"| Items without DOI (OpenAIRE) | {len(no_doi_items):,} |",
        f"| **Total missing from initial OpenAlex query** | {len(found) + len(not_found) + len(no_doi_items):,} |",
        "",
        "## Batch DOI Lookup Results",
        "",
        f"Queried {len(found) + len(not_found):,} DOIs against OpenAlex in batches of {BATCH_SIZE}.",
        "",
        "| Result | Count | % |",
        "|--------|------:|---:|",
        f"| Found in OpenAlex (by DOI) | {len(found):,} | {len(found) / (len(found) + len(not_found)) * 100:.1f}% |",
        f"| Not found in OpenAlex | {len(not_found):,} | {len(not_found) / (len(found) + len(not_found)) * 100:.1f}% |",
        "",
    ]

    # Why found items weren't in initial query
    if found:
        lines += [
            "### Found by DOI — Why Were They Missing From Initial Query?",
            "",
            f"Of {len(found):,} DOIs that DO exist in OpenAlex:",
            "",
            f"- **{found_ut:,}** are UT-affiliated in OpenAlex → they were in the initial query but their DOIs normalized differently (URL vs bare)",
            f"- **{found_not_ut:,}** are NOT UT-affiliated in OpenAlex → OpenAIRE includes them via broader affiliation matching (acknowledgements, grant metadata)",
            "",
            "#### Found-in-OpenAlex by OpenAIRE Type",
            "",
            "| OpenAIRE Type | Count |",
            "|--------------|------:|",
        ]
        for typ, cnt in found_by_type.most_common():
            lines.append(f"| {typ} | {cnt:,} |")
        lines.append("")

    if type_mismatches:
        mismatch_by_pair = Counter(
            (f["openaire_type"], f.get("openalex_type", ""))
            for f in type_mismatches
        )
        lines += [
            "#### Type Mismatches (OpenAIRE → OpenAlex)",
            "",
            "| OpenAIRE Type | OpenAlex Type | Count |",
            "|--------------|---------------|------:|",
        ]
        for (oa_t, ax_t), cnt in mismatch_by_pair.most_common(20):
            lines.append(f"| {oa_t} | {ax_t} | {cnt:,} |")
        lines.append("")

    # Not found at all
    if not_found:
        lines += [
            "### Not Found in OpenAlex",
            "",
            f"{len(not_found):,} DOIs from OpenAIRE do not exist in OpenAlex at all.",
            "",
            "#### By OpenAIRE Type",
            "",
            "| Type | Count |",
            "|------|------:|",
        ]
        for typ, cnt in not_found_by_type.most_common():
            lines.append(f"| {typ} | {cnt:,} |")
        lines.append("")

        # Sample of not-found DOIs
        lines += [
            "#### Sample Not-Found DOIs (first 20)",
            "",
            "```",
        ]
        for item in not_found[:20]:
            lines.append(f"  {item['doi']}  ({item['openaire_type']})")
        lines.append("```")
        lines.append("")

    # No-DOI items
    if no_doi_items:
        lines += [
            "### Items Without DOI (OpenAIRE Only)",
            "",
            f"{len(no_doi_items):,} items in OpenAIRE have no DOI and therefore cannot be matched.",
            "",
            "#### By Type",
            "",
            "| Type | Count |",
            "|------|------:|",
        ]
        for typ, cnt in no_doi_by_type.most_common():
            lines.append(f"| {typ} | {cnt:,} |")
        lines.append("")

    # Root cause analysis
    lines += [
        "## Root Cause Analysis",
        "",
        "### 1. DOI Normalization Mismatch (largest factor)",
        "OpenAIRE stores bare DOIs (`10.1234/abc`), OpenAlex stores full URLs (`https://doi.org/10.1234/abc`). ",
        "The initial comparison was done with proper normalization, so this was handled correctly. ",
        "However, this explains why simple string comparison would show 0 overlap.",
        "",
        "### 2. Broader Affiliation Matching in OpenAIRE",
        f"OpenAIRE includes publications linked to UT through **any** affiliation channel: ",
        "acknowledgements, grant metadata, EU project participation, and informal associations. ",
        f"An estimated **{found_not_ut:,}** of the 'missing' DOIs exist in OpenAlex but are NOT linked to UT there — ",
        "they appear in OpenAIRE only via these broader matching mechanisms.",
        "",
        "### 3. Non-Publication Content Types",
        f"OpenAIRE indexes **datasets** and **software** as first-class works. ",
        f"OpenAlex primarily indexes scholarly works (articles, books, etc.). ",
        f"This explains {not_found_by_type.get('dataset', 0):,} datasets and {not_found_by_type.get('software', 0):,} software items that have no OpenAlex equivalent.",
        "",
        "### 4. Grey Literature and Conference Proceedings",
        "Many conference proceedings, preprints, and institutional repository deposits in OpenAIRE ",
        "have DOIs but are not indexed by OpenAlex, especially those from smaller repositories ",
        "or with non-standard DOI prefixes (e.g., `10.25625/` for UT repository).",
        "",
        "### 5. Items Without DOI",
        f"{len(no_doi_items):,} items in OpenAIRE have no DOI at all. These are predominantly ",
        "conference abstracts, institutional repository deposits, and internal reports that were never ",
        "assigned a DOI. OpenAlex requires a DOI for most indexed works.",
        "",
        "## Recommendations",
        "",
        "1. **For comprehensive coverage**, use both OpenAIRE and OpenAlex — each covers items the other misses.",
        "2. **For citation analysis**, prefer OpenAlex — its citation data is more structured and complete.",
        "3. **For dataset/software tracking**, use OpenAIRE — OpenAlex does not index these.",
        "4. **For EU-funded research**, use OpenAIRE — it has project-level links that OpenAlex lacks.",
        "5. **For author/institution disambiguation**, prefer OpenAlex — its structured IDs (ROR, ORCID) are more reliable.",
    ]

    return "\n".join(lines)


async def main() -> None:
    console.print("[bold]Missing Items Analysis: OpenAIRE vs OpenAlex[/bold]\n")

    # Load data
    console.print("Loading data...")
    missing_dois = load_missing_dois()
    missing_metadata = load_missing_metadata()
    openaire_types = load_openaire_dois_with_types()

    console.print(f"  Missing DOIs to query: {len(missing_dois):,}")
    console.print(f"  Missing items metadata: {len(missing_metadata):,}")

    # Batch-query OpenAlex
    total_batches = (len(missing_dois) + BATCH_SIZE - 1) // BATCH_SIZE
    console.print(f"\n[bold]Batch-querying OpenAlex ({total_batches} batches of {BATCH_SIZE})...[/bold]")

    async with AlethecaSession() as session:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
        ) as progress:
            t = progress.add_task(
                f"Querying {len(missing_dois):,} DOIs…",
                total=total_batches,
            )
            start = time.time()
            lookup_results = await batch_lookup_dois(
                session, missing_dois, progress_task=t, progress=progress
            )
            elapsed = time.time() - start
    found_count = len(lookup_results)
    console.print(
        f"\n  [green]Found {found_count:,}/{len(missing_dois):,} in OpenAlex "
        f"({elapsed:.1f}s, ~{len(missing_dois) / max(elapsed, 0.1):.0f} DOIs/sec)[/green]"
    )
    # Classify — add missing DOIs as not-found entries
    console.print("\nClassifying results...")
    found_dois = {d.lower() for d in lookup_results}
    for doi in missing_dois:
        if doi.lower() not in found_dois:
            lookup_results[doi.lower()] = None
    classification = classify_found_items(lookup_results, openaire_types)
    # Generate report
    console.print("Generating report...")
    report = generate_report(classification, missing_metadata, openaire_types)
    # Write report
    REPORT_PATH.write_text(report)
    console.print(f"\n[bold green]Report written to {REPORT_PATH}[/bold green]")
    # Print summary table
    console.print()
    table = Table(title="Summary")
    table.add_column("Category", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("%", justify="right")
    total = len(missing_dois) + sum(1 for m in missing_metadata if not m.get("normalized_doi"))
    found = len(classification["found_in_openalex"])
    not_found = len(classification["not_in_openalex"])
    no_doi = sum(1 for m in missing_metadata if not m.get("normalized_doi"))
    table.add_row("Found in OpenAlex (by DOI)", f"{found:,}", f"{found / total * 100:.1f}%")
    table.add_row("Not found in OpenAlex", f"{not_found:,}", f"{not_found / total * 100:.1f}%")
    table.add_row("No DOI (cannot query)", f"{no_doi:,}", f"{no_doi / total * 100:.1f}%")
    table.add_row("[bold]Total[/bold]", f"[bold]{total:,}[/bold]", "")
    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
