# Contributing

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/utsmok/aletheca.git
cd aletheca
uv sync --all-groups
```

This installs the package in editable mode with the `dev` group (pytest, pytest-asyncio, pytest-httpx, ruff, ty) and the `docs` group (mkdocs, mkdocs-material, mkdocstrings).

## Tests

```bash
uv run pytest              # unit tests, fast and offline
uv run pytest -m live_api  # live OpenAlex smoke tests; needs ALETHECA_API_KEY
```

The unit suite uses pytest-httpx and never touches the network. Tests marked `live_api` are deselected by default (`asyncio_mode = "auto"`, so async tests need no markers).

## Lint, types, format

```bash
uv run ruff check --fix
uv run ruff format
uv run ty check src
```

## Docs

```bash
uv run mkdocs serve        # local preview
uv run mkdocs build --strict
```

The API reference pages are generated from the source with mkdocstrings; docstrings are user-facing text.

## Releases

Keep a Changelog format in `CHANGELOG.md`. Branch `overhaul-2026-11` carries the current overhaul work.
