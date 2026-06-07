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
    mo.md(
        """
# Convenience Queries

Aletheca bundles common multi-step workflows into convenience
query functions accessible via `session.queries`.
"""
    )


@app.cell
async def _(mo, session):
    _ = mo.md("## Works by Author Name")

    _works = await session.queries.works_by_author("Yann LeCun", limit=5)
    _rows = []
    for _w in _works:
        _title = _w.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Year": _w.publication_year or "N/A",
                "Citations": _w.cited_by_count,
            }
        )
    _count_md = mo.md(f'**{len(_works)}** works found for "Yann LeCun"\n')
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_, _count_md, _table])


@app.cell
async def _(mo, session):
    _ = mo.md("## Works by Institution Name")

    _works = await session.queries.works_by_institution("ETH Zurich", limit=5)
    _rows = []
    for _w in _works:
        _title = _w.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Year": _w.publication_year or "N/A",
                "Citations": _w.cited_by_count,
            }
        )
    _count_md = mo.md(f'**{len(_works)}** works found for "ETH Zurich"\n')
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_, _count_md, _table])


@app.cell
async def _(mo, session):
    _ = mo.md("## Works by DOI")

    _works = await session.queries.works_by_doi(
        ["10.1038/s41586-019-1234-0", "10.1126/science.aar7186"],
    )
    _rows = []
    for _w in _works:
        _title = _w.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "DOI": _w.doi or "N/A",
                "Year": _w.publication_year or "N/A",
            }
        )
    _count_md = mo.md(f"**{len(_works)}** works found by DOI\n")
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_, _count_md, _table])


@app.cell
async def _(mo, session):
    _ = mo.md("## Citing Works")

    citing = await session.queries.citing_works("W2741809807", limit=5)
    _rows = []
    for _w in citing:
        _title = _w.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Year": _w.publication_year or "N/A",
                "Citations": _w.cited_by_count,
            }
        )
    _count_md = mo.md(f"**{len(citing)}** works that cite W2741809807 (capped at 5 for display)\n")
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_, _count_md, _table])


@app.cell
async def _(mo, session):
    _ = mo.md("## Referenced Works")

    referenced = await session.queries.referenced_works("W2741809807", limit=5)
    _rows = []
    for _w in referenced:
        _title = _w.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Year": _w.publication_year or "N/A",
                "Citations": _w.cited_by_count,
            }
        )
    _count_md = mo.md(
        f"**{len(referenced)}** works referenced by W2741809807 "
        f"(capped at 5 for display)\n"
    )
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_, _count_md, _table])


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
