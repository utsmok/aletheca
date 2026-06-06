# Syntheca Example Scripts

This directory contains example scripts demonstrating how to use the Syntheca library. Every example is also a **marimo notebook** — they can be run as scripts, explored interactively, or embedded in documentation.

## Examples

- **`simple_example.py`** — Basic usage: fetch a work by DOI, search works with filters, and iterate through results.

## Running Examples

### As a script

```bash
uv run examples/simple_example.py
```

### As an interactive marimo notebook

```bash
uv run marimo run examples/simple_example.py
```

### Edit interactively

```bash
uv run marimo edit examples/simple_example.py
```

### In WASM (browser, no Python needed)

```bash
uv run marimo export html-wasm examples/simple_example.py -o site/simple_example --mode run
```

## No API Key Required

The OpenAlex API works without authentication via its [polite pool](https://docs.openalex.org/how-to-use-the-pool/get-your-api-key/polite-pool). All examples run without credentials. Set the `SYNTHECA_EMAIL` environment variable to your email address to identify yourself and get higher rate limits:

```bash
export SYNTHECA_EMAIL=you@example.com
```

## Embedding in Documentation

### Via molab (recommended)

The easiest way to embed interactive notebooks in docs is via [molab](https://docs.marimo.io/guides/molab/). For notebooks hosted on GitHub:

```html
<iframe
    src="https://marimo.app/github/YOUR_USER/aletheca/blob/main/examples/simple_example.py/wasm?embed=true"
    sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms"
    width="100%"
    height="600"
    style="border: 1px solid #ddd; border-radius: 8px;"
></iframe>
```

### Via marimo islands

For embedding individual cell outputs directly in documentation pages:

```python
from marimo import MarimoIslandGenerator

generator = MarimoIslandGenerator.from_file(
    "examples/simple_example.py",
    display_code=False,
)
html = generator.render_html()
```

See the [marimo islands docs](https://docs.marimo.io/guides/exporting/webassembly_html/#embed-marimo-outputs-in-html-using-islands) for full details.

### Via self-hosted WASM HTML

Export and serve the notebook as a self-contained HTML file:

```bash
uv run marimo export html-wasm examples/simple_example.py -o docs/examples/simple_example.html --mode run
```

Then embed with an iframe in your documentation site.
