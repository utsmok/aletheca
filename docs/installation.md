# Installation

## Requirements

- **Python 3.12+** — syntheca uses modern type syntax (`X | Y` unions, generic type params) that requires 3.12 or newer.
- **pip** or **[uv](https://docs.astral.sh/uv/)** package manager.

## Install

=== "pip"

    ```bash
    pip install syntheca
    ```

=== "uv"

    ```bash
    uv add syntheca
    ```

=== "pipx (for scripts)"

    ```bash
    pipx install syntheca
    ```

## Verify installation

```python
import syntheca

print(syntheca.__version__)
```

## Optional dependencies

Syntheca keeps its core dependency footprint small (`bibliofabric` + `pydantic`). Additional analysis packages are available as an extra:

```bash
pip install "syntheca[analysis]"
```

This pulls in:

| Package | Purpose |
|---|---|
| `polars` | Fast DataFrames |
| `duckdb` | In-process analytical database |
| `pandas` | Traditional DataFrames |
| `numpy` | Numerical computing |
| `matplotlib` | Plotting |
| `pyarrow` | Columnar data interchange |
| `rich` | Terminal formatting |

??? note "Why an extra, not separate packages?"
    Analysis workflows are common enough to bundle, but not everyone needs a full data science stack. The `[analysis]` extra lets you opt in without pulling hundreds of megabytes into lightweight deployment environments.

## From source

```bash
git clone https://github.com/utsmok/syntheca.git
cd syntheca
uv sync --all-groups   # install all dev/doc/test dependencies
```

See [Contributing](contributing.md) for the full development setup.
