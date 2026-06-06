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
    from syntheca.endpoints import (
        AuthorsFilters,
        InstitutionsFilters,
        WorksFilters,
    )

    return AuthorsFilters, InstitutionsFilters, SynthecaSession, WorksFilters


@app.cell
def _():
    session = SynthecaSession()
    return (session,)


@app.cell
async def _(mo):
    mo.md(
        """
    # Filtering and Search

    Syntheca provides typed Pydantic filter models for every endpoint.
    This notebook demonstrates how to combine filters, use the `search`
    parameter, and query different entity types.
    """
    )


@app.cell
async def _(SynthecaSession, WorksFilters, mo, session):
    mo.md("## Works Filters")

    filters = WorksFilters(
        publication_year=2024,
        is_oa=True,
        type="article",
        language="en",
    )

    response = await session.works.search(
        page=1,
        page_size=5,
        filters=filters,
        search="machine learning",
    )

    total = response.meta.count if response.meta else 0
    mo.md(
        f'**Open-access English articles from 2024** matching "machine learning": '
        f"**{total:,}** results"
    )
    return filters, response, total


@app.cell
def _(mo, response):
    mo.md("### Top Results")

    rows = []
    for work in (response.results or [])[:5]:
        title = work.title or "No title"
        rows.append(
            {
                "Title": title[:80],
                "Year": work.publication_year or "N/A",
                "Citations": work.cited_by_count,
                "OA": work.open_access and work.open_access.oa_status or "N/A",
            }
        )
    mo.ui.table(rows, selection=None)
    return (rows,)


@app.cell
async def _(AuthorsFilters, mo, session):
    mo.md("## Author Search by Name")

    author_filters = AuthorsFilters(display_name_search="Geoffrey Hinton")
    author_resp = await session.authors.search(
        page=1, page_size=5, filters=author_filters
    )

    author_rows = []
    for author in (author_resp.results or [])[:5]:
        author_rows.append(
            {
                "Name": author.display_name or "N/A",
                "Works": author.works_count,
                "Cited by": author.cited_by_count,
                "ORCID": author.orcid or "N/A",
            }
        )
    mo.ui.table(author_rows, selection=None)
    return author_filters, author_resp, author_rows


@app.cell
async def _(InstitutionsFilters, mo, session):
    mo.md("## Institutions by Country")

    inst_filters = InstitutionsFilters(country_code="CH", type="education")
    inst_resp = await session.institutions.search(
        page=1, page_size=5, filters=inst_filters
    )

    inst_rows = []
    for inst in (inst_resp.results or [])[:5]:
        inst_rows.append(
            {
                "Name": inst.display_name or "N/A",
                "Country": inst.country_code or "N/A",
                "Type": inst.type or "N/A",
                "Works": inst.works_count,
            }
        )
    mo.ui.table(inst_rows, selection=None)
    return inst_filters, inst_resp, inst_rows


@app.cell
async def _(WorksFilters, mo, session):
    mo.md("## Combining Multiple Filters")

    combined = WorksFilters(
        publication_year=2023,
        is_oa=True,
        has_abstract=True,
        type="article",
    )

    resp = await session.works.search(
        page=1,
        page_size=3,
        filters=combined,
        search="large language models",
    )

    n = resp.meta.count if resp.meta else 0
    mo.md(f"**{n:,}** open-access articles from 2023 with abstracts about LLMs")
    return combined, resp, n


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
