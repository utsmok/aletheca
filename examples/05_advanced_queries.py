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
# Advanced Queries

Cursor pagination, field selection, sorting, dot-notation filters,
and maximum-throughput page sizes.
"""
    )


@app.cell
async def _(mo, session):
    _heading = mo.md("## Cursor Pagination with `iterate`")

    count = 0
    async for _work in session.works.iterate(
        page_size=200,
        filters=WorksFilters(publication_year=2024, type="article", is_oa=True),
    ):
        count += 1
        if count >= 500:
            break

    _result = mo.md(f"Iterated through **{count}** open-access 2024 articles (capped at 500)")
    mo.vstack([_heading, _result])
    return (count,)


@app.cell
async def _(mo, session):
    _heading = mo.md("## Sort Results")

    _resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(publication_year=2024),
        sort_by="cited_by_count:desc",
    )

    _rows = []
    for _work in (_resp.results or [])[:5]:
        _title = _work.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Citations": _work.cited_by_count,
                "Year": _work.publication_year or "N/A",
            }
        )
    _subheading = mo.md("### Most-cited works of 2024\n")
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_heading, _subheading, _table])
    return _resp, _rows


@app.cell
async def _(mo, session):
    _heading = mo.md("## Sort by Publication Date (Ascending)")

    _resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(publication_year=2024, type="article"),
        sort_by="publication_date:asc",
    )

    _rows = []
    for _work in (_resp.results or [])[:5]:
        _title = _work.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Date": _work.publication_date or "N/A",
                "Citations": _work.cited_by_count,
            }
        )
    _subheading = mo.md("### Earliest published articles of 2024\n")
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_heading, _subheading, _table])
    return (_rows,)


@app.cell
async def _(mo, session):
    _heading = mo.md("## Dot-Notation Filters (authorships.author.id)")

    _resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(authorships_author_id="A5023888391"),
        sort_by="cited_by_count:desc",
    )

    _total = _resp.meta.count if _resp.meta else 0
    _rows = []
    for _work in (_resp.results or [])[:5]:
        _title = _work.title or "No title"
        _rows.append(
            {
                "Title": _title[:80],
                "Year": _work.publication_year or "N/A",
                "Citations": _work.cited_by_count,
            }
        )
    _info = mo.md(f"**{_total:,}** works by author A5023888391. Top 5:\n")
    _table = mo.ui.table(_rows, selection=None)
    mo.vstack([_heading, _info, _table])
    return _resp, _rows, _total


@app.cell
async def _(mo, session):
    _heading = mo.md("## Maximum Throughput (per_page=200)")

    _resp = await session.works.search(
        page=1,
        page_size=200,
        filters=WorksFilters(publication_year=2024, is_oa=True),
    )

    page_count = len(_resp.results or [])
    _total = _resp.meta.count if _resp.meta else 0
    _info = mo.md(
        f"Fetched **{page_count}** results in a single request "
        f"(per_page=200) out of **{_total:,}** total.\n\n"
        f"Use cursor pagination (`iterate`) to retrieve all results "
        f"without hitting page limits."
    )
    mo.vstack([_heading, _info])
    return page_count, _resp, _total


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
