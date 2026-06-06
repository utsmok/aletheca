# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aletheca",
#     "certifi",
#     "marimo",
# ///
import marimo

__generated_with = "0.0.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from aletheca import AlethecaSession
    from aletheca.endpoints import AuthorsFilters, WorksFilters

    return AuthorsFilters, AlethecaSession, WorksFilters


@app.cell
def _():
    session = AlethecaSession()
    return (session,)


@app.cell
async def _(mo):
    mo.md(
        """
    # Author Discovery

    Search for authors by name, inspect their metadata, and retrieve
    their published works.
    """
    )


@app.cell
async def _(AuthorsFilters, mo, session):
    mo.md("## Search for an Author")

    filters = AuthorsFilters(display_name_search="Yann LeCun")
    resp = await session.authors.search(page=1, page_size=5, filters=filters)

    author = (resp.results or [])[0] if resp.results else None

    if author:
        mo.md(
            f"**{author.display_name}**\n\n"
            f"- **ORCID:** {author.orcid or 'N/A'}\n"
            f"- **Works:** {author.works_count:,}\n"
            f"- **Cited by:** {author.cited_by_count:,}\n"
            f"- **Affiliations:** "
            + ", ".join(a.display_name or "N/A" for a in author.affiliations[:3])
        )
    else:
        mo.md("No author found.")
    return author, filters, resp


@app.cell
async def _(mo, session):
    mo.md("## Author Details (h-index, i10-index)")

    author = await session.authors.get("A5023888391")

    stats = author.summary_stats
    if stats:
        mo.md(
            f"**{author.display_name}** — Summary Stats\n\n"
            f"- **h-index:** {stats.h_index}\n"
            f"- **i10-index:** {stats.i10_index}\n"
            f"- **2yr mean citedness:** {stats.two_yr_mean_citedness}\n"
        )
    else:
        mo.md("No summary stats available.")
    return author, stats


@app.cell
async def _(mo, session):
    mo.md("## Author Affiliations")

    author = await session.authors.get("A5023888391")
    aff_rows = []
    for aff in author.affiliations[:10]:
        aff_rows.append(
            {
                "Institution": aff.display_name or "N/A",
                "Country": aff.country_code or "N/A",
                "Type": aff.type or "N/A",
                "Years": aff.years
                and ", ".join(str(y.year) for y in aff.years[:5])
                or "N/A",
            }
        )
    mo.ui.table(aff_rows, selection=None)
    return (aff_rows,)


@app.cell
async def _(WorksFilters, mo, session):
    mo.md("## Get an Author's Works")

    works_filters = WorksFilters(authorships_author_id="A5023888391")
    works_resp = await session.works.search(
        page=1,
        page_size=5,
        filters=works_filters,
        sort="cited_by_count:desc",
    )

    total = works_resp.meta.count if works_resp.meta else 0
    work_rows = []
    for work in (works_resp.results or [])[:5]:
        title = work.title or "No title"
        work_rows.append(
            {
                "Title": title[:80],
                "Year": work.publication_year or "N/A",
                "Citations": work.cited_by_count,
            }
        )
    mo.md(f"**{total:,}** total works. Top 5 by citation count:\n")
    mo.ui.table(work_rows, selection=None)
    return total, work_rows, works_filters, works_resp


@app.cell
async def _(mo, session):
    mo.md("## Convenience: `works_by_author`")

    works = await session.queries.works_by_author(session, "Yann LeCun", limit=5)
    mo.md(f"Retrieved **{len(works)}** works via `session.queries.works_by_author`")
    return (works,)


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
