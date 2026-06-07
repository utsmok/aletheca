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

    return (mo,)


@app.cell
def _():
    from aletheca import AlethecaSession
    from aletheca.endpoints import WorksFilters

    return AlethecaSession, WorksFilters


@app.cell
def _():
    session = AlethecaSession()
    return (session,)


@app.cell
async def _(mo):
    _ = mo.md(
"""
# Iterator Helpers

Aletheca provides `collect`, `count`, and `first` helpers
for common patterns — so you don't need to manually paginate.
"""
    )


@app.cell
async def _(WorksFilters, mo, session):
    _ = mo.md("## `count()` — Total Without Downloading")

    _filters = WorksFilters(publication_year=2024, is_oa=True, type="article")
    total = await session.works.count(filters=_filters)

    mo.md(f"**{total:,}** open-access articles published in 2024")
    return _filters, total


@app.cell
async def _(WorksFilters, mo, session):
    _ = mo.md("## `first()` — Top Result with Sort")

    _filters = WorksFilters(publication_year=2024, type="article")
    top = await session.works.first(filters=_filters, sort_by="cited_by_count:desc")

    if top:
        _ = mo.md(
            f"### Most-cited article of 2024\n\n"
            f"**{top.title}**\n\n"
            f"- **Citations:** {top.cited_by_count:,}\n"
            f"- **DOI:** {top.doi or 'N/A'}\n"
            f"- **Type:** {top.type or 'N/A'}\n"
        )
    else:
        _ = mo.md("No result found.")
    return (top,)


@app.cell
async def _(WorksFilters, mo, session):
    _ = mo.md("## `collect()` — Gather Results Into a List")

    _filters = WorksFilters(
        publication_year=2024,
        type="article",
        is_oa=True,
    )
    works = await session.works.collect(filters=_filters, limit=20)

    mo.md(f"Collected **{len(works)}** works into a list (limit=20)")
    return _filters, works


@app.cell
def _(mo, works):
    _ = mo.md("### Collected Works")

    rows = []
    for w in works[:10]:
        _title = w.title or "No title"
        rows.append(
            {
                "Title": _title[:80],
                "Year": w.publication_year or "N/A",
                "Citations": w.cited_by_count,
            }
        )
    mo.ui.table(rows, selection=None)
    return (rows,)


@app.cell
async def _(WorksFilters, mo, session):
    _ = mo.md("## Manual Iteration vs. Helpers")

    _filters = WorksFilters(publication_year=2024, is_oa=True)

    mo.md(
        "**Manual iteration:**\n\n"
        "```python\n"
        "count = 0\n"
        "async for work in session.works.iterate(filters=filters, page_size=50):\n"
        "    count += 1\n"
        "    if count >= 100:\n"
        "        break\n"
        "```\n\n"
        "**Using `collect()`:**\n\n"
        "```python\n"
        "works = await session.works.collect(filters=filters, limit=100)\n"
        "```\n\n"
        "The helper is shorter and handles cursor pagination internally."
    )


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
