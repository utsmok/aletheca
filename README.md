# Aletheca
A Python library to interact with the OpenAlex API, providing tools for data retrieval, modeling, and analysis of scholarly entities.

## Features
- Easy access to OpenAlex API endpoints
- Validation, serialization, and more for all OpenAlex entities
- Built with performance and usability in mind
- Efficient and elegant data retrieval methods: pagination, filtering, and bulk fetching are all handled for you
- But if you want to get your hands dirty, low-level API access is also available
- Extensive configuration options to set up the library to your needs

# Dev instructions

use `uv` to manage the environment and dependencies:

```bash
> uv run main.py
> uv run pytest
> uv add polars
> uv remove polars
> uv sync -U
> uv sync --all-groups
```

use `ruff` and `ty` for linting, formatting, checking:

```bash
> uv run ruff check .
> uv run ruff format .
> uv run ty check .
```

