import marimo

__generated_with = "0.17.8"
app = marimo.App(
    width="columns",
    layout_file="layouts/check_entity_dataclasses.grid.json",
)


@app.cell(hide_code=True)
def _():
    import httpx
    from aletheca.entities import (
        Work,
        Author,
        Source,
        Topic,
        Concept,
        Publisher,
        Institution,
        Funder,
    )
    from rich import print
    from rich.pretty import Pretty
    from collections import defaultdict
    import marimo as mo

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
    return Pretty, defaultdict, httpx, mapping, mo, print


@app.cell(hide_code=True)
def _(mapping, mo):
    new_sample = mo.ui.run_button(kind="success", label="🔄️ Click to refresh API data.")
    selection = mo.ui.multiselect(options=list(mapping.keys()), label="Select entity types to fetch", value=list(mapping.keys()))
    num_to_retrieve = mo.ui.number(label="Number of entities to retrieve per type", value=1, start=1, stop=10)
    mo.vstack(
        [
            selection,
            num_to_retrieve,
            new_sample
        ]
    )
    return new_sample, num_to_retrieve, selection


@app.cell(hide_code=True)
def _(defaultdict, httpx, mo, new_sample, num_to_retrieve, print, selection):
    if new_sample.value:
        base_url = "https://api.openalex.org/"
        data = defaultdict(list)
        with httpx.Client() as client:
            for ent_type in mo.status.progress_bar(selection.value*num_to_retrieve.value,
                title="Fetching example data from the OpenAlex API",
            ):
                try:
                    data[ent_type].append(client.get(f"{base_url}{ent_type}s/random").json())
                except Exception as e:
                    print(f"Error fetching {ent_type}: {e}")
    return (data,)


@app.cell(hide_code=True)
def _(mo, num_to_retrieve):
    selected_result = mo.ui.number(
        label="Select which result to display (1-indexed)",
        value=1,
        start=1,
        stop=num_to_retrieve.value,
    )
    selected_result
    return (selected_result,)


@app.cell(hide_code=True)
def _(Pretty, errors, mo, num_to_retrieve, parsed_data, selected_result):
    output = [mo.md("## No data retrieved yet.")]

    if parsed_data:
        show = mo.vstack(
            [
                mo.ui.tabs(
                    {
                        str(res_type).capitalize(): mo.hstack(
                            [
                                mo.vstack(
                                    [mo.md("Raw API data (dict)"), Pretty(parsed_result[selected_result.value-1][0])]
                                ),
                                mo.vstack(
                                    [mo.md("Parsed as nested dataclass"), Pretty(parsed_result[selected_result.value-1][1])]
                                ),
                            ]
                        )
                        for res_type, parsed_result in parsed_data.items()
                    }
                )
            ]
        )
        msg = f"## result {selected_result.value}/{num_to_retrieve.value} of each entity type is shown below."
        if errors:
            msg += " Some entities failed to parse. See tabes marked with ❌."
        
        output = [mo.md(msg), show]

    mo.vstack(output)
    return


@app.cell(hide_code=True)
def _(data, defaultdict, mapping, new_sample, print):
    errors = []
    wrong_data = {}
    parsed_data = defaultdict(list)

    if new_sample.value:
        errors = []
        for ent, ent_datas in data.items():
            entity_class = mapping[ent]
            for ent_data in ent_datas:
                try:
                    parsed_data["✅ " + ent].append([ent_data, entity_class.from_dict(ent_data)])
                except Exception as e:
                    print(f"Error parsing entity {ent}: {e}")
                    parsed_data["❌ " + ent].append([ent_data, None])

    return errors, parsed_data


if __name__ == "__main__":
    app.run()
