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
    mo.md("## Cursor Pagination with `iterate`")

    count = 0
    async for work in session.works.iterate(
        page_size=200,
        filters=WorksFilters(publication_year=2024, type="article", is_oa=True),
    ):
        count += 1
        if count >= 500:
            break

    mo.md(f"Iterated through **{count}** open-access 2024 articles (capped at 500)")
    return (count,)


@app.cell
async def _(mo, session):
    mo.md("## Sort Results")

    resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(publication_year=2024),
        sort="cited_by_count:desc",
    )

    rows = []
    for work in (resp.results or [])[:5]:
        title = work.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Citations": work.cited_by_count,
                "Year": work.publication_year or "N/A",
            }
        )
    mo.md("### Most-cited works of 2024\n")
    mo.ui.table(rows, selection=None)
    return resp, rows


@app.cell
async def _(mo, session):
    mo.md("## Sort by Publication Date (Ascending)")

    resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(publication_year=2024, type="article"),
        sort="publication_date:asc",
    )

    rows = []
    for work in (resp.results or [])[:5]:
        title = work.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Date": work.publication_date or "N/A",
                "Citations": work.cited_by_count,
            }
        )
    mo.md("### Earliest published articles of 2024\n")
    mo.ui.table(rows, selection=None)
    return (rows,)


@app.cell
async def _(mo, session):
    mo.md("## Dot-Notation Filters (authorships.author.id)")

    resp = await session.works.search(
        page=1,
        page_size=5,
        filters=WorksFilters(authorships_author_id="A5023888391"),
        sort="cited_by_count:desc",
    )

    total = resp.meta.count if resp.meta else 0
    rows = []
    for work in (resp.results or [])[:5]:
        title = work.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": work.publication_year or "N/A",
                "Citations": work.cited_by_count,
            }
        )
    mo.md(f"**{total:,}** works by author A5023888391. Top 5:\n")
    mo.ui.table(rows, selection=None)
    return resp, rows, total


@app.cell
async def _(mo, session):
    mo.md("## Maximum Throughput (per_page=200)")

    resp = await session.works.search(
        page=1,
        page_size=200,
        filters=WorksFilters(publication_year=2024, is_oa=True),
    )

    page_count = len(resp.results or [])
    total = resp.meta.count if resp.meta else 0
    mo.md(
        f"Fetched **{page_count}** results in a single request "
        f"(per_page=200) out of **{total:,}** total.\n\n"
        f"Use cursor pagination (`iterate`) to retrieve all results "
        f"without hitting page limits."
    )
    return page_count, resp, total


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
