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
    from aletheca._helpers import (
        detect_id_type,
        normalize_doi,
        parse_openalex_id,
        reconstruct_abstract,
    )
    from aletheca.models import SafeList, SafeStr

    return (
        SafeList,
        SafeStr,
        AlethecaSession,
        detect_id_type,
        normalize_doi,
        parse_openalex_id,
        reconstruct_abstract,
    )


@app.cell
def _():
    session = AlethecaSession()
    return (session,)


@app.cell
async def _(mo):
    mo.md(
        """
    # Safe Types and Helpers

    Aletheca ships `SafeList` and `SafeStr` types that make API data
    safe to traverse without null checks, plus utility helpers for
    common identifier operations.
    """
    )


@app.cell
async def _(mo, session):
    mo.md("## SafeList — Iterate Without Null Checks")

    work = await session.works.get("W2741809807")

    author_rows = []
    for a in work.authorships:
        author_rows.append(
            {
                "Position": a.author_position or "N/A",
                "Name": a.author and a.author.get("display_name", "N/A") or "N/A",
                "Is corresponding": a.is_corresponding,
            }
        )

    mo.md(
        f"Work has **{len(work.authorships)}** authorships — "
        f"no null-check needed on the list itself:\n"
    )
    mo.ui.table(author_rows, selection=None)
    return author_rows, work


@app.cell
async def _(mo, session):
    mo.md("## SafeStr — String Methods on Nullable Fields")

    work = await session.works.get("W2741809807")

    # SafeStr coerces None → "", so string methods never raise
    doi = work.doi
    mo.md(
        f"- **DOI (raw):** `{doi}`\n"
        f"- **DOI uppercased:** `{doi.upper()}`\n"
        f"- **DOI starts with 'https':** `{doi.startswith('https')}`\n"
        f"- **DOI length:** `{len(doi)}`\n\n"
        f"`SafeStr` fields always return a string, even when the "
        f"API returns `null`."
    )
    return (doi,)


@app.cell
def _(mo, normalize_doi):
    mo.md("## `normalize_doi()` — Strip URL Prefix")

    examples = [
        "https://doi.org/10.1038/s41586-019-1234-0",
        "http://doi.org/10.1126/science.abc123",
        "doi.org/10.1000/xyz123",
        "10.1234/test",
    ]

    rows = []
    for raw in examples:
        rows.append({"Input": raw, "Normalized": normalize_doi(raw)})

    mo.ui.table(rows, selection=None)
    return examples, rows


@app.cell
def _(mo, parse_openalex_id):
    mo.md("## `parse_openalex_id()` — Extract Short ID from URL")

    examples = [
        "https://openalex.org/W2741809807",
        "W2741809807",
        "https://openalex.org/A5023888391",
        "I136233082",
    ]

    rows = []
    for raw in examples:
        rows.append({"Input": raw, "Parsed": parse_openalex_id(raw)})

    mo.ui.table(rows, selection=None)
    return examples, rows


@app.cell
def _(detect_id_type, mo):
    mo.md("## `detect_id_type()` — Identify Identifier Type")

    examples = [
        "W2741809807",
        "A5023888391",
        "I136233082",
        "10.1038/s41586-019-1234-0",
        "https://doi.org/10.1038/s41586-019-1234-0",
        "0000-0002-1825-0097",
        "https://orcid.org/0000-0002-1825-0097",
    ]

    rows = []
    for raw in examples:
        rows.append({"Identifier": raw, "Type": detect_id_type(raw) or "unknown"})

    mo.ui.table(rows, selection=None)
    return examples, rows


@app.cell
async def _(mo, reconstruct_abstract, session):
    mo.md("## `reconstruct_abstract()` — Inverted Index to Text")

    work = await session.works.get("W2741809807")

    if work.abstract_inverted_index:
        abstract = reconstruct_abstract(work.abstract_inverted_index)
        mo.md(
            f"### Reconstructed Abstract\n\n"
            f"{abstract[:500]}{'...' if abstract and len(abstract) > 500 else ''}"
        )
    else:
        mo.md("No abstract available for this work.")

    # Or use the convenience property:
    mo.md("\n\nYou can also use `work.reconstructed_abstract` as a shortcut.")
    return (abstract,)


@app.cell
async def _(session):
    await session.close()


if __name__ == "__main__":
    app.run()
