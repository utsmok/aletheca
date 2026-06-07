# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aletheca",
#     "certifi",
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.0.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
# Aletheca Quick Start

**Switch to code view with Ctrl+. to see all code cells**

This notebook demonstrates basic usage of Aletheca for retrieving
and searching OpenAlex scholarly data.
"""
    )
    return (mo,)


@app.cell
def _():
    from aletheca import AlethecaSession
    from aletheca.endpoints import WorksFilters

    session = AlethecaSession()
    return WorksFilters, session


@app.cell
async def _(mo, session):
    _heading = mo.md("## 📄 Get a Single Work by ID")

    _work = await session.works.get("W4237179648")
    _info = mo.md(
        f"**Title:** {_work.title or 'N/A'}\n\n"
        f"**Year:** {_work.publication_year or 'N/A'}\n\n"
        f"**DOI:** {_work.doi or 'N/A'}\n\n"
        f"**Type:** {_work.type or 'N/A'}\n\n"
        f"**Cited by:** {_work.cited_by_count}"
    )
    mo.vstack([_heading, _info])
    return (_work,)


@app.cell
async def _(mo, session):
    _heading = mo.md("## 📄 Get a Work by DOI")

    try:
        doi_work = await session.works.get("https://doi.org/10.1038/s41586-021-03819-2")
        _result = mo.md(f"**Found:** {doi_work.title}")
    except Exception as e:
        _result = mo.md(f"**Error:** {e}")
    mo.vstack([_heading, _result])
    return (doi_work,)


@app.cell
async def _(WorksFilters, mo, session):
    _heading = mo.md("## 🔍 Search Works with Filters")

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

    _count_md = mo.md(f"Found **{total_results}** total results")
    mo.vstack([_heading, _count_md])
    return filters, response, total_results


@app.cell
def _(mo, response):
    _heading = mo.md("### Results Table")

    rows = []
    for _work in (response.results or [])[:5]:
        _title = _work.title or "No title"
        rows.append(
            {
                "Title": _title[:80] if len(_title) > 80 else _title,
                "Year": _work.publication_year or "N/A",
                "Type": _work.type or "Unknown",
                "Citations": _work.cited_by_count,
            }
        )

    _table = mo.ui.table(rows, selection=None)
    mo.vstack([_heading, _table])
    return (rows,)


@app.cell
async def _(filters, mo, session):
    _heading = mo.md("## 🔄 Iterate Through Results")

    count = 0
    async for _work in session.works.iterate(page_size=10, filters=filters):
        count += 1
        if count >= 25:
            break

    _result = mo.md(f"Processed **{count}** works (capped at 25)")
    mo.vstack([_heading, _result])
    return (count,)


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
