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
    _ = mo.md(r"""
    # Institution Research

    Fetch an institution by ID, retrieve its works, and analyse its
    research output and topics.
    """)


@app.cell
async def _(mo, session):
    _ = mo.md("## Fetch Institution by ID")

    _inst = await session.institutions.get("I136233082")
    summary = (
        f"**{_inst.display_name}**\n\n"
        f"- **Country:** {_inst.country_code or 'N/A'}\n"
        f"- **Type:** {_inst.type or 'N/A'}\n"
        f"- **Homepage:** {_inst.homepage_url or 'N/A'}\n"
        f"- **ROR:** {_inst.ror or 'N/A'}\n"
        f"- **Works count:** {_inst.works_count:,}\n"
        f"- **Cited by:** {_inst.cited_by_count:,}\n"
    )
    _ = mo.md(summary)
    return _inst, summary


@app.cell
async def _(mo, session):
    _ = mo.md("## Associated Institutions")

    _inst = await session.institutions.get("I136233082")
    _rows = []
    for assoc in _inst.associated_institutions[:10]:
        _rows.append(
            {
                "Name": assoc.display_name or "N/A",
                "Type": assoc.type or "N/A",
                "Country": assoc.country_code or "N/A",
                "Relationship": assoc.relationship or "N/A",
            }
        )
    _ = mo.ui.table(_rows, selection=None)
    return (_rows,)


@app.cell
async def _(WorksFilters, mo, session):
    _ = mo.md("## Recent Works from This Institution")

    filters = WorksFilters(
        authorships_institutions_id="I136233082",
        publication_year=2024,
        type="article",
    )

    resp = await session.works.search(
        page=1, page_size=10, filters=filters, sort="cited_by_count:desc"
    )

    total = resp.meta.count if resp.meta else 0
    work_rows = []
    for work in (resp.results or [])[:10]:
        title = work.title or "No title"
        work_rows.append(
            {
                "Title": title[:80],
                "Year": work.publication_year or "N/A",
                "Citations": work.cited_by_count,
                "Type": work.type or "N/A",
            }
        )
    _ = mo.md(f"**{total:,}** articles from 2024\n")
    _ = mo.ui.table(work_rows, selection=None)
    return filters, resp, total, work_rows


@app.cell
async def _(mo, session):
    _ = mo.md("## Topic Distribution")

    _inst = await session.institutions.get("I136233082")
    _topic_rows = []
    for t in _inst.topics[:10]:
        _topic_rows.append(
            {
                "Topic": t.display_name or "N/A",
                "Works": t.works_count,
                "Subfield": t.subfield and t.subfield.display_name or "N/A",
                "Field": t.field and t.field.display_name or "N/A",
            }
        )
    _ = mo.ui.table(_topic_rows, selection=None)
    return (_topic_rows,)


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
