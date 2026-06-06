# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "syntheca",
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
    from syntheca import SynthecaSession
    from syntheca.endpoints import WorksFilters

    return SynthecaSession, WorksFilters


@app.cell
def _():
    session = SynthecaSession()
    return (session,)


@app.cell
async def _(mo):
    mo.md(
        """
    # Convenience Queries

    Syntheca bundles common multi-step workflows into convenience
    query functions accessible via `session.queries`.
    """
    )


@app.cell
async def _(mo, session):
    mo.md("## Works by Author Name")

    works = await session.queries.works_by_author(session, "Yann LeCun", limit=5)
    rows = []
    for w in works:
        title = w.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": w.publication_year or "N/A",
                "Citations": w.cited_by_count,
            }
        )
    mo.md(f'**{len(works)}** works found for "Yann LeCun"\n')
    mo.ui.table(rows, selection=None)
    return rows, works


@app.cell
async def _(mo, session):
    mo.md("## Works by Institution Name")

    works = await session.queries.works_by_institution(session, "ETH Zurich", limit=5)
    rows = []
    for w in works:
        title = w.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": w.publication_year or "N/A",
                "Citations": w.cited_by_count,
            }
        )
    mo.md(f'**{len(works)}** works found for "ETH Zurich"\n')
    mo.ui.table(rows, selection=None)
    return rows, works


@app.cell
async def _(mo, session):
    mo.md("## Works by DOI")

    works = await session.queries.works_by_doi(
        session,
        ["10.1038/s41586-019-1234-0", "10.1126/science.aar7186"],
    )
    rows = []
    for w in works:
        title = w.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "DOI": w.doi or "N/A",
                "Year": w.publication_year or "N/A",
            }
        )
    mo.md(f"**{len(works)}** works found by DOI\n")
    mo.ui.table(rows, selection=None)
    return rows, works


@app.cell
async def _(mo, session):
    mo.md("## Citing Works")

    citing = await session.queries.citing_works(session, "W2741809807", limit=5)
    rows = []
    for w in citing:
        title = w.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": w.publication_year or "N/A",
                "Citations": w.cited_by_count,
            }
        )
    mo.md(f"**{len(citing)}** works that cite W2741809807 (capped at 5 for display)\n")
    mo.ui.table(rows, selection=None)
    return citing, rows


@app.cell
async def _(mo, session):
    mo.md("## Referenced Works")

    referenced = await session.queries.referenced_works(session, "W2741809807", limit=5)
    rows = []
    for w in referenced:
        title = w.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": w.publication_year or "N/A",
                "Citations": w.cited_by_count,
            }
        )
    mo.md(
        f"**{len(referenced)}** works referenced by W2741809807 "
        f"(capped at 5 for display)\n"
    )
    mo.ui.table(rows, selection=None)
    return referenced, rows


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
