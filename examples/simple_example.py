import marimo

__generated_with = "0.0.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
    # Syntheca Quick Start

    **Switch to code view with Ctrl+. to see all code cells**

    This notebook demonstrates basic usage of Syntheca for retrieving
    and searching OpenAlex scholarly data.
    """
    )
    return (mo,)


@app.cell
def _():
    from syntheca import SynthecaSession
    from syntheca.endpoints import WorksFilters

    session = SynthecaSession()
    return WorksFilters, session


@app.cell
async def _(mo, session):
    mo.md("## 📄 Get a Single Work by ID")

    work = await session.works.get("W4237179648")
    mo.md(
        f"**Title:** {work.title or 'N/A'}\n\n"
        f"**Year:** {work.publication_year or 'N/A'}\n\n"
        f"**DOI:** {work.doi or 'N/A'}\n\n"
        f"**Type:** {work.type or 'N/A'}\n\n"
        f"**Cited by:** {work.cited_by_count}"
    )
    return (work,)


@app.cell
async def _(mo, session):
    mo.md("## 📄 Get a Work by DOI")

    try:
        doi_work = await session.works.get("https://doi.org/10.1038/s41586-021-03819-2")
        mo.md(f"**Found:** {doi_work.title}")
    except Exception as e:
        mo.md(f"**Error:** {e}")
    return (doi_work,)


@app.cell
async def _(WorksFilters, mo, session):
    mo.md("## 🔍 Search Works with Filters")

    filters = WorksFilters(
        publication_year=2024,
        is_oa=True,
        type="article",
    )

    response = await session.works.search(
        page=1, page_size=5, filters=filters, search="quantum computing"
    )

    total_results = (
        response.meta.count if response.meta else len(response.results or [])
    )

    mo.md(f"Found **{total_results}** total results")
    return filters, response, total_results


@app.cell
def _(mo, response):
    mo.md("### Results Table")

    rows = []
    for work in (response.results or [])[:5]:
        title = work.title or "No title"
        rows.append(
            {
                "Title": title[:80] if len(title) > 80 else title,
                "Year": work.publication_year or "N/A",
                "Type": work.type or "Unknown",
                "Citations": work.cited_by_count,
            }
        )

    mo.ui.table(rows, selection=None)
    return (rows,)


@app.cell
async def _(filters, mo, session):
    mo.md("## 🔄 Iterate Through Results")

    count = 0
    async for work in session.works.iterate(page_size=10, filters=filters):
        count += 1
        if count >= 25:
            break

    mo.md(f"Processed **{count}** works (capped at 25)")
    return (count,)


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
