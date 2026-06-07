#!/usr/bin/env python3
"""Comprehensive analysis of University of Twente research output (2023-2025).

Fetches ALL publications from OpenAlex for UT, stores them in DuckDB, runs
analytics, and produces matplotlib visualisations. Designed as a direct
comparison with the AIREloom (OpenAIRE) analysis script.

Run with:
    uv run --extra analysis examples/comprehensive_analysis.py
"""

from __future__ import annotations

import asyncio
import statistics
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aletheca import AlethecaSession, Work
from aletheca.endpoints import WorksFilters

# ── Configuration ──────────────────────────────────────────────────────────

# OpenAlex institution ID for University of Twente
UT_OPENALEX_ID = "https://openalex.org/I94624287"
DATE_FROM = "2023-01-01"
DATE_TO = "2025-12-31"

OUTPUT_DIR = Path("output")
DB_PATH = OUTPUT_DIR / "analysis.duckdb"

console = Console()

# ── DuckDB schema & storage ────────────────────────────────────────────────

_PUB_SCHEMA = """
    id              VARCHAR PRIMARY KEY,
    title           VARCHAR,
    doi             VARCHAR,
    type            VARCHAR,
    publication_date VARCHAR,
    publication_year INTEGER,
    publisher       VARCHAR,
    language        VARCHAR,
    is_open_access  BOOLEAN,
    oa_status       VARCHAR,
    open_access_url VARCHAR,
    citation_count  INTEGER,
    journal_name    VARCHAR,
    license         VARCHAR,
    author_names    VARCHAR,
    topics          VARCHAR,
    keywords        VARCHAR,
    countries       VARCHAR,
    funders         VARCHAR,
    institutions_count INTEGER"""


def _init_db(con: duckdb.DuckDBPyConnection) -> None:
    for name, schema in [
        ("publications", _PUB_SCHEMA),
    ]:
        con.execute(f"DROP TABLE IF EXISTS {name}")
        con.execute(f"CREATE TABLE {name} ({schema})")


def _pub_to_row(p: Work) -> dict:
    author_names = "; ".join(
        (a.author or {}).get("display_name", "")
        for a in p.authorships
        if (a.author or {}).get("display_name")
    )
    topics = "; ".join(
        t.display_name or ""
        for t in p.topics
        if t.display_name
    )
    keywords = "; ".join(
        k.display_name or ""
        for k in p.keywords
        if k.display_name
    )
    # Countries from authorships
    countries = "; ".join(
        c
        for a in p.authorships
        for c in a.countries
        if c
    )
    funders = "; ".join(
        f.display_name or ""
        for f in p.funders
        if f.display_name
    )
    # Journal/source name from primary_location
    journal = ""
    if p.primary_location and p.primary_location.source:
        journal = (p.primary_location.source.get("display_name") or "")
    elif p.locations:
        for loc in p.locations:
            if loc.source and loc.source.get("display_name"):
                journal = loc.source["display_name"]
                break

    # Publisher from primary_location source
    publisher = ""
    if p.primary_location and p.primary_location.source:
        publisher = (p.primary_location.source.get("host_organization_name") or "")

    # OA fields
    is_oa = p.open_access.is_oa if p.open_access else False
    oa_status = str(p.open_access.oa_status or "") if p.open_access else ""
    oa_url = str(p.open_access.oa_url or "") if p.open_access else ""
    license_val = ""
    if p.best_oa_location and p.best_oa_location.license:
        license_val = str(p.best_oa_location.license)

    # DOI from ids or top-level
    doi = str(p.doi or "")
    if not doi and p.ids and p.ids.doi:
        doi = str(p.ids.doi)

    return {
        "id": p.id or "",
        "title": (p.title or "")[:500],
        "doi": doi,
        "type": str(p.type or ""),
        "publication_date": str(p.publication_date or ""),
        "publication_year": p.publication_year or 0,
        "publisher": publisher,
        "language": str(p.language or ""),
        "is_open_access": is_oa,
        "oa_status": oa_status,
        "open_access_url": oa_url,
        "citation_count": p.cited_by_count or 0,
        "journal_name": journal,
        "license": license_val,
        "author_names": author_names,
        "topics": topics,
        "keywords": keywords,
        "countries": countries,
        "funders": funders,
        "institutions_count": p.institutions_distinct_count or 0,
    }


def _store_batch(
    con: duckdb.DuckDBPyConnection,
    table: str,
    rows: list[dict],
    clear: bool = True,
) -> None:
    if not rows:
        return
    df = pl.DataFrame(rows)
    if clear:
        con.execute(f"DELETE FROM {table}")
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO {table}({cols}) SELECT * FROM df")


# ── Data retrieval ─────────────────────────────────────────────────────────


async def fetch_data(con: duckdb.DuckDBPyConnection) -> dict:
    """Fetch all data from OpenAlex and persist to DuckDB."""
    data: dict = {}

    async with AlethecaSession() as session:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
        ) as progress:
            # ── Counts ──
            t = progress.add_task("Counting UT publications (2023-2025)…", total=None)
            base_filters = WorksFilters(
                authorships_institutions_id=UT_OPENALEX_ID,
                from_publication_date=DATE_FROM,
                to_publication_date=DATE_TO,
            )
            total_pubs = await session.works.count(filters=base_filters)
            oa_filters = WorksFilters(
                authorships_institutions_id=UT_OPENALEX_ID,
                from_publication_date=DATE_FROM,
                to_publication_date=DATE_TO,
                is_oa=True,
            )
            total_oa = await session.works.count(filters=oa_filters)
            progress.update(
                t,
                completed=1,
                total=1,
                description=f"UT 2023-2025: {total_pubs:,} pubs ({total_oa:,} OA)",
            )
            data["total_publications"] = total_pubs
            data["total_open_access"] = total_oa

            # ── Publications (ALL, cursor-paginated) ──
            t = progress.add_task(
                f"Fetching all {total_pubs:,} publications…",
                total=None,
            )
            filters = WorksFilters(
                authorships_institutions_id=UT_OPENALEX_ID,
                from_publication_date=DATE_FROM,
                to_publication_date=DATE_TO,
            )
            publications = await session.works.collect(
                filters=filters,
                page_size=200,
                sort_by="publication_date:desc",
            )
            progress.update(
                t,
                completed=1,
                total=1,
                description=f"Got {len(publications):,} publications",
            )
            data["publications"] = publications
        # Persist
        _store_batch(con, "publications", [_pub_to_row(p) for p in publications])
    return data


# ── Analytics ──────────────────────────────────────────────────────────────


def run_analytics(con: duckdb.DuckDBPyConnection) -> dict:
    """Run SQL analytics on the stored data."""
    r: dict = {}

    # Publication type distribution
    r["type_dist"] = con.execute("""
        SELECT type, count(*) as n FROM publications
        GROUP BY type ORDER BY n DESC
    """).fetchall()

    # Year trends
    r["year_trends"] = con.execute("""
        SELECT publication_year, count(*) as n FROM publications
        WHERE publication_year > 0
        GROUP BY publication_year ORDER BY publication_year
    """).fetchall()

    # Top authors
    r["top_authors"] = con.execute("""
        SELECT t.author, count(*) as n
        FROM publications, unnest(string_split(author_names, '; ')) AS t(author)
        WHERE t.author != ''
        GROUP BY t.author ORDER BY n DESC LIMIT 15
    """).fetchall()

    # Open access stats
    oa = con.execute("""
        SELECT count(*), sum(CASE WHEN is_open_access THEN 1 ELSE 0 END)
        FROM publications
    """).fetchone()
    r["oa_stats"] = {"total": oa[0], "oa": oa[1]}

    # OA status distribution
    r["oa_status_dist"] = con.execute("""
        SELECT oa_status, count(*) as n FROM publications
        WHERE oa_status IS NOT NULL AND oa_status != ''
        GROUP BY oa_status ORDER BY n DESC
    """).fetchall()

    # Top cited
    r["top_cited"] = con.execute("""
        SELECT title, doi, citation_count, publication_year FROM publications
        WHERE citation_count > 0 ORDER BY citation_count DESC LIMIT 10
    """).fetchall()

    # Top topics
    r["top_topics"] = con.execute("""
        SELECT lower(trim(t.tp)) as topic, count(*) as n
        FROM publications, unnest(string_split(topics, '; ')) AS t(tp)
        WHERE t.tp != '' GROUP BY topic ORDER BY n DESC LIMIT 20
    """).fetchall()

    # ── OA trend by year ──
    r["oa_trend"] = con.execute("""
        SELECT publication_year,
               count(*) as total,
               sum(CASE WHEN is_open_access THEN 1 ELSE 0 END) as oa_count,
               round(100.0 * sum(CASE WHEN is_open_access THEN 1 ELSE 0 END) / count(*), 1) as oa_pct
        FROM publications
        WHERE publication_year > 0
        GROUP BY publication_year ORDER BY publication_year
    """).fetchall()

    # ── Top publishers ──
    r["top_publishers"] = con.execute("""
        SELECT publisher, count(*) as n FROM publications
        WHERE publisher IS NOT NULL AND publisher != ''
        GROUP BY publisher ORDER BY n DESC LIMIT 10
    """).fetchall()

    # ── Country collaboration ──
    r["country_collab"] = con.execute("""
        SELECT t.cc, count(*) as n
        FROM publications, unnest(string_split(countries, '; ')) AS t(cc)
        WHERE t.cc != ''
        GROUP BY t.cc ORDER BY n DESC LIMIT 15
    """).fetchall()

    # ── Top publication venues (journals) ──
    r["top_journals"] = con.execute("""
        SELECT journal_name, count(*) as n FROM publications
        WHERE journal_name IS NOT NULL AND journal_name != ''
        GROUP BY journal_name ORDER BY n DESC LIMIT 15
    """).fetchall()

    # ── Type by year cross-tab ──
    r["type_by_year"] = con.execute("""
        SELECT publication_year, type, count(*) as n
        FROM publications
        WHERE publication_year > 0
        GROUP BY publication_year, type
        ORDER BY publication_year, n DESC
    """).fetchall()

    # ── Citation statistics ──
    citation_rows = con.execute("""
        SELECT citation_count FROM publications
        WHERE citation_count IS NOT NULL AND citation_count > 0
    """).fetchall()
    all_cites = [row[0] for row in citation_rows]

    cite_by_type = con.execute("""
        SELECT type,
               count(*) as n,
               round(avg(citation_count), 1) as mean_cites,
               max(citation_count) as max_cites
        FROM publications
        WHERE citation_count IS NOT NULL AND citation_count > 0
        GROUP BY type ORDER BY mean_cites DESC
    """).fetchall()

    median_cite = statistics.median(all_cites) if all_cites else 0
    mean_cite = statistics.mean(all_cites) if all_cites else 0
    max_cite = max(all_cites) if all_cites else 0
    r["citation_stats"] = {
        "overall": {
            "n_with_citations": len(all_cites),
            "mean": round(mean_cite, 1),
            "median": round(median_cite, 1),
            "max": max_cite,
        },
        "by_type": cite_by_type,
        "_raw_citations": all_cites,
    }

    # ── Language distribution ──
    r["lang_dist"] = con.execute("""
        SELECT language, count(*) as n FROM publications
        WHERE language IS NOT NULL AND language != ''
        GROUP BY language ORDER BY n DESC LIMIT 10
    """).fetchall()

    # ── Funder distribution ──
    r["funder_dist"] = con.execute("""
        SELECT lower(trim(t.f)) as funder, count(*) as n
        FROM publications, unnest(string_split(funders, '; ')) AS t(f)
        WHERE t.f != ''
        GROUP BY funder ORDER BY n DESC LIMIT 15
    """).fetchall()

    # ── Institutions count distribution ──
    r["inst_count_dist"] = con.execute("""
        SELECT
            CASE
                WHEN institutions_count = 1 THEN '1 (single)'
                WHEN institutions_count BETWEEN 2 AND 3 THEN '2-3'
                WHEN institutions_count BETWEEN 4 AND 10 THEN '4-10'
                WHEN institutions_count > 10 THEN '11+'
                ELSE 'unknown'
            END as bucket,
            count(*) as n
        FROM publications
        GROUP BY bucket ORDER BY n DESC
    """).fetchall()

    return r


# ── Visualisation ──────────────────────────────────────────────────────────


def _save(fig: plt.Figure, name: str) -> Path:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_plots(analytics: dict) -> list[Path]:
    """Generate matplotlib plots and return saved file paths."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    palette = ["#2563eb", "#7c3aed", "#059669", "#dc2626", "#d97706", "#0891b2"]

    # 1 — Publications by year
    year_data = analytics["year_trends"]
    if year_data:
        years, counts = zip(*year_data, strict=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar([str(y) for y in years], counts, color="#2563eb", edgecolor="white")
        ax.set_xlabel("Year")
        ax.set_ylabel("Publications")
        ax.set_title("UT Publications by Year (2023-2025) — OpenAlex")
        for y, c in zip(years, counts, strict=False):
            ax.annotate(
                str(c),
                (str(y), c),
                textcoords="offset points",
                xytext=(0, 4),
                ha="center",
                fontsize=9,
            )
        paths.append(_save(fig, "publications_by_year.png"))

    # 2 — Type + Open Access overview
    type_data = analytics["type_dist"]
    oa = analytics["oa_stats"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    if type_data:
        labels, vals = zip(*type_data, strict=False)
        ax1.barh(labels, vals, color=palette[: len(labels)])
        ax1.set_xlabel("Count")
        ax1.set_title("Publication Types")
        for i, v in enumerate(vals):
            ax1.text(v + 1, i, f"{v:,}", va="center", fontsize=9)

    if oa["total"]:
        oa_pct = oa["oa"] / oa["total"] * 100
        ax2.pie(
            [oa_pct, 100 - oa_pct],
            labels=["Open Access", "Other"],
            autopct="%1.1f%%",
            colors=["#059669", "#94a3b8"],
            startangle=90,
        )
        ax2.set_title(f"Open Access ({oa['oa']:,} / {oa['total']:,})")

    fig.suptitle(
        "Publication Overview — University of Twente (2023-2025)\nOpenAlex",
        fontweight="bold",
    )
    paths.append(_save(fig, "publication_overview.png"))

    # 3 — Top-cited publications
    top_cited = analytics["top_cited"]
    if top_cited:
        titles = [r[0][:55] + ("…" if len(r[0]) > 55 else "") for r in top_cited]
        cites = [r[2] for r in top_cited]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(range(len(titles)), cites, color="#7c3aed")
        ax.set_yticks(range(len(titles)))
        ax.set_yticklabels(titles, fontsize=8)
        ax.set_xlabel("Citations")
        ax.set_title("Top-10 Cited Publications — OpenAlex")
        ax.invert_yaxis()
        for i, v in enumerate(cites):
            ax.text(v + 1, i, f"{v:,}", va="center", fontsize=8)
        paths.append(_save(fig, "top_cited.png"))

    # 4 — OA trend by year
    oa_trend = analytics.get("oa_trend", [])
    if oa_trend:
        years, totals, oa_counts, oa_pcts = zip(*oa_trend, strict=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            [str(y) for y in years],
            oa_pcts,
            "o-",
            color="#059669",
            linewidth=2,
            markersize=8,
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Open Access %")
        ax.set_title("Open Access Trend by Year — OpenAlex")
        ax.set_ylim(0, 100)
        for y, pct, n_oa, n_tot in zip(years, oa_pcts, oa_counts, totals, strict=False):
            ax.annotate(
                f"{pct}%\n({n_oa:,}/{n_tot:,})",
                (str(y), pct),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=9,
            )
        paths.append(_save(fig, "oa_trend.png"))

    # 5 — Top publishers
    top_publishers = analytics.get("top_publishers", [])
    if top_publishers:
        pub_names, pub_vals = zip(*top_publishers, strict=False)
        pub_labels = [n[:50] + "…" if len(n) > 50 else n for n in pub_names]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(pub_labels, pub_vals, color="#0891b2")
        ax.set_xlabel("Publications")
        ax.set_title("Top 10 Publishers — OpenAlex")
        ax.invert_yaxis()
        for i, v in enumerate(pub_vals):
            ax.text(v + 1, i, f"{v:,}", va="center", fontsize=9)
        paths.append(_save(fig, "top_publishers.png"))

    # 6 — Type distribution pie
    if type_data:
        labels, vals = zip(*type_data, strict=False)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            vals,
            labels=labels,
            autopct="%1.1f%%",
            colors=palette[: len(labels)],
            startangle=90,
        )
        ax.set_title("Publication Type Distribution — OpenAlex")
        paths.append(_save(fig, "type_distribution.png"))

    # 7 — Citation distribution histogram
    cite_raw = analytics.get("citation_stats", {}).get("_raw_citations", [])
    cite_overall = analytics.get("citation_stats", {}).get("overall", {})
    n_with = cite_overall.get("n_with_citations", 0)
    if n_with > 0 and cite_raw:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(cite_raw, bins=50, color="#7c3aed", edgecolor="white")
        ax.set_xlabel("Citation Count")
        ax.set_ylabel("Number of Publications")
        ax.set_title("Citation Count Distribution — OpenAlex")
        if max(cite_raw) > 100:
            ax.set_yscale("log")
        paths.append(_save(fig, "citation_distribution.png"))

    # 8 — OA status breakdown
    oa_status_data = analytics.get("oa_status_dist", [])
    if oa_status_data:
        labels, vals = zip(*oa_status_data, strict=False)
        colors_map = {
            "diamond": "#059669",
            "gold": "#d97706",
            "green": "#2563eb",
            "hybrid": "#7c3aed",
            "bronze": "#cd7f32",
            "closed": "#94a3b8",
        }
        colors = [colors_map.get(l, "#6b7280") for l in labels]
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(vals, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.set_title("Open Access Status Distribution — OpenAlex")
        paths.append(_save(fig, "oa_status_distribution.png"))

    return paths


# ── Reporting ──────────────────────────────────────────────────────────────


def _table(
    title: str,
    rows: list[tuple],
    col_names: list[str],
    col_styles: list[str] | None = None,
) -> Table:
    """Build a Rich table with uniform styling."""
    t = Table(title=title, show_lines=False)
    styles = col_styles or (["cyan"] + ["green"] * (len(col_names) - 1))
    for name, style in zip(col_names, styles, strict=False):
        t.add_column(name, style=style, justify="right" if style != "cyan" else "left")
    for row in rows:
        t.add_row(*(str(c) for c in row))
    return t


def print_report(data: dict, analytics: dict, plot_paths: list[Path]) -> None:
    """Print executive summary to Rich console."""
    total = data.get("total_publications", 0)
    total_oa = data.get("total_open_access", 0)
    oa_pct = total_oa / total * 100 if total else 0
    fetched = len(data.get("publications", []))

    console.print(
        Panel(
            f"[bold]University of Twente — OpenAlex Research Analytics (2023-2025)[/bold]\n\n"
            f"  Total publications in OpenAlex (2023-2025): {total:,}\n"
            f"  Total open access:                          {total_oa:,} ({oa_pct:.1f}%)\n"
            f"  Publications fetched:                       {fetched:,}",
            title="Executive Summary",
            border_style="blue",
        )
    )

    console.print(
        _table(
            "Publication Types",
            [(t, f"{n:,}") for t, n in analytics.get("type_dist", [])],
            ["Type", "Count"],
        )
    )

    console.print(
        _table(
            "Publications by Year",
            [(str(y), f"{n:,}") for y, n in analytics.get("year_trends", [])],
            ["Year", "Count"],
        )
    )

    console.print(
        _table(
            "Top Authors",
            [(a, f"{n:,}") for a, n in analytics.get("top_authors", [])[:10]],
            ["Author", "Pubs"],
        )
    )

    console.print(
        _table(
            "Top-Cited Publications",
            [
                (t[:60], str(y or ""), f"{c:,}")
                for t, doi, c, y in analytics.get("top_cited", [])[:10]
            ],
            ["Title", "Year", "Citations"],
            ["cyan", "green", "yellow"],
        )
    )

    console.print(
        _table(
            "Top Topics",
            [(kw, f"{n:,}") for kw, n in analytics.get("top_topics", [])[:15]],
            ["Topic", "Count"],
        )
    )

    # OA trend
    oa_trend = analytics.get("oa_trend", [])
    if oa_trend:
        console.print(
            _table(
                "Open Access Trend by Year",
                [
                    (str(y), f"{tot:,}", f"{oa_n:,}", f"{pct}%")
                    for y, tot, oa_n, pct in oa_trend
                ],
                ["Year", "Total", "OA Count", "OA %"],
                ["cyan", "green", "yellow", "magenta"],
            )
        )

    # OA status
    oa_status = analytics.get("oa_status_dist", [])
    if oa_status:
        console.print(
            _table(
                "Open Access Status Distribution",
                [(s, f"{n:,}") for s, n in oa_status],
                ["Status", "Count"],
            )
        )

    # Top publishers
    top_publishers = analytics.get("top_publishers", [])
    if top_publishers:
        console.print(
            _table(
                "Top Publishers",
                [(p[:60], f"{n:,}") for p, n in top_publishers],
                ["Publisher", "Pubs"],
            )
        )

    # Country collaboration
    country_collab = analytics.get("country_collab", [])
    if country_collab:
        console.print(
            _table(
                "Country Collaboration (Top 15)",
                [(c, f"{n:,}") for c, n in country_collab],
                ["Country", "Pubs"],
            )
        )

    # Top journals
    top_journals = analytics.get("top_journals", [])
    if top_journals:
        console.print(
            _table(
                "Top Publication Venues (Top 15)",
                [(j[:60], f"{n:,}") for j, n in top_journals],
                ["Journal", "Pubs"],
            )
        )

    # Citation statistics
    cite_stats = analytics.get("citation_stats", {})
    cite_overall = cite_stats.get("overall", {})
    if cite_overall:
        console.print(
            _table(
                "Citation Statistics",
                [
                    (
                        "Papers with citations",
                        f"{cite_overall.get('n_with_citations', 0):,}",
                    ),
                    ("Mean citations", str(cite_overall.get("mean", 0))),
                    ("Median citations", str(cite_overall.get("median", 0))),
                    ("Max citations", f"{cite_overall.get('max', 0):,}"),
                ],
                ["Metric", "Value"],
            )
        )

    cite_by_type = cite_stats.get("by_type", [])
    if cite_by_type:
        console.print(
            _table(
                "Citation Statistics by Type",
                [
                    (t, f"{n:,}", str(mean), f"{mx:,}")
                    for t, n, mean, mx in cite_by_type
                ],
                ["Type", "Papers", "Mean Citations", "Max Citations"],
                ["cyan", "green", "yellow", "magenta"],
            )
        )

    # Language distribution
    lang_dist = analytics.get("lang_dist", [])
    if lang_dist:
        console.print(
            _table(
                "Top Languages",
                [(lang, f"{n:,}") for lang, n in lang_dist],
                ["Language", "Pubs"],
            )
        )

    # Funder distribution
    funder_dist = analytics.get("funder_dist", [])
    if funder_dist:
        console.print(
            _table(
                "Top Funders",
                [(f[:60], f"{n:,}") for f, n in funder_dist],
                ["Funder", "Pubs"],
            )
        )

    console.print("\n[bold]Generated outputs:[/bold]")
    console.print(f"  Database:  {DB_PATH}")
    for p in plot_paths:
        console.print(f"  Plot:      {p}")
    console.print()


# ── Main ───────────────────────────────────────────────────────────────────


async def main() -> None:
    console.print(
        Panel(
            "[bold]Aletheca Comprehensive Analysis[/bold]\n"
            "University of Twente (2023-2025) — OpenAlex",
            border_style="blue",
        )
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    _init_db(con)

    try:
        data = await fetch_data(con)
        analytics = run_analytics(con)
        plot_paths = generate_plots(analytics)
        print_report(data, analytics, plot_paths)
    finally:
        con.close()

    console.print("[bold green]Analysis complete.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
