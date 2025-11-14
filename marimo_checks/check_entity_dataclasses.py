import marimo

__generated_with = "0.17.8"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo
    import httpx
    import polars
    from aletheca.entities import (
        Work,
        Author,
        Source,
        Topic,
        Concept,
        Publisher,
        Institution,
        Funder,
        PagedResponse,
        Keyword,
    )
    from rich import print
    return (
        Author,
        Concept,
        Funder,
        Institution,
        Publisher,
        Source,
        Topic,
        Work,
        httpx,
        print,
    )


@app.cell
def _(
    Author,
    Concept,
    Funder,
    Institution,
    Publisher,
    Source,
    Topic,
    Work,
    httpx,
    print,
):
    base_url = "https://api.openalex.org/"
    mapping = {
        "work": Work,
        "author": Author,
        "source": Source,
        "topic": Topic,
        "concept": Concept,
        "publisher": Publisher,
        "institution": Institution,
        "funder": Funder,
    }
    data = {}
    with httpx.Client() as client:
        for ent_type in ["work", "author", "source", "topic", "concept", "publisher", "institution", "funder"]:
            try:
                data[ent_type] = client.get(f"{base_url}{ent_type}s/random").json()
            except Exception as e:
                print(f"Error fetching {ent_type}: {e}")
    return data, mapping


@app.cell
def _(data, mapping, print):
    parsed_data = {}
    for ent, ent_data in data.items():
        entity_class = mapping[ent]
        try:
            parsed_data[ent] = entity_class(**ent_data)
        except Exception as e:
            print(f"Error parsing {ent}: {e}")
    return (parsed_data,)


@app.cell
def _(parsed_data, print):
    for entity_type, entity in parsed_data.items():
        print(entity)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
