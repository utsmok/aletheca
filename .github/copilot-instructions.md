## Aletheca — Copilot instructions

Be concise and make edits that match existing styles and typing. Use these repository-specific notes to make PR-ready changes.

This project is a Python library to interact with the OpenAlex API, providing tools for data retrieval, modeling, and analysis of scholarly entities.

Basic libraries for this API exist (like `pyalex`), but this project aims to provide a more user-friendly, performant, and configurable interface for common tasks, while still allowing low-level access when needed, and include fully typed interfaces for all entities and operations.

- Project layout: package code lives in `src/aletheca/`. Current key modules:
  - `entities.py` — canonical dataclasses for OpenAlex entities (Work, Author, Source, etc.). Prefer adding/adjusting typed dataclasses here when modeling API responses.
  - `api.py` — HTTP client logic and request/response handling for OpenAlex. See below for more details.
  - `endpoints.py` — endpoint path and parameter definitions: like filters and field selections for each endpoint etc. Most will be directly linked to an entity as defined in `entities.py`; but there are some other endpoints with different response shapes (e.g. autocomplete and aboutness) that should be defined here. Also needs to handle endpoints that group/facet data instead of returning raw entities.
  - `config.py` — central default & user settings (api_base_url, timeouts, retries). User-configurable settings should go here. Should support reading from environment variables/yaml/etc in the future.
  - `utils.py` — helpers (doi normalization, parsing). Many functions are placeholders — prefer minimal, well-tested implementations. If utils get too complex, consider moving logic elsewhere.

- Important patterns and examples:
  - Dataclasses are the current canonical shape for entities (see `src/aletheca/entities.py`). Keep fields typed and use `field(default_factory=...)` for mutable defaults.
  - We will probably move to different models (like `pydantic`) in the future to incorporate validation, serialization, and other features; but for now, dataclasses are sufficient.
  - Field names should mirror the OpenAlex API exactly. If the API uses non-Pythonic names (e.g. `2yr_mean_citedness`), map them to a Pythonic alias (see `SummaryStats` in `entities.py` which uses `two_yr_mean_citedness`).
  - There is a small check script at `marimo_checks/check_entity_dataclasses.py` used to validate the core entity dataclass shapes. It is a `marimo` notebook, and should not be run by itself, only by the user manually using `uv run marimo edit marimo_checks/check_entity_dataclasses.py`.

- Developer workflows :
  - Environment/deps: the project uses `uv` (see `pyproject.toml`).
  - **NEVER** use `python`, `pip`, or `venv` directly; always use `uv` to ensure consistency:
    - instead of `python main.py` use `uv run main.py`
    - instead of `pip install package` use `uv add package`
    - instead of `pip uninstall package` use `uv remove package`
    - you will never need to manually create or activate a venv; `uv` handles that for you when you call `uv run`, `uv add`, `uv remove`, or `uv sync`.
    - for syncing dependencies, use `uv sync` to install from `pyproject.toml` [+ optionally -U for update] or `uv sync --all-groups` to install all optional groups [and update them if -U is passed]. During development, sync all groups.
  - tests should be run with `uv run pytest` (see `tests/`); prefer small, focused unit tests and mock network calls where possible. We will also accept integration tests that hit the real API, but keep them separate from unit tests. How we exactly will structure the tests is to be determined.
  - There are currently no tests implemented yet.

- Formatting, typing, and packaging notes:
  - The package exposes `py.typed` (PEP 561); preserve type annotations and imports so downstream type checkers work.
  - Dataclasses should be instantiated with keyword arguments; avoid the use of positional args. For API deserialization always use unpacking (`**dict`).
  - use `ruff` and `ty` for linting, formatting, checking:
    ```bash
    > uv run ruff check .
    > uv run ruff format .
    > uv run ty check .
    ```

- Retrieving data from OpenAlex API:
  - HTTP interactions belong in `api.py`.
  - The idea is to create a specific Client class for this module, based on `httpx.Client` that uses a config from `config.py` to manage settings and default parameters like timeouts, retries, base URL, user email address, default paging setup, etc.
  - The core rate limits and other API concerns should be defined in `config.py` (user-editable if needed).
  - Specific query parameters like filter options and field selection should be defined per-endpoint in `endpoints.py`, which should then be passed to specific Client methods to construct requests.
  - There will also be several utility functions to assist in constructing requests, like normalizing/validating input, batching queries with lists of IDs, etc.
  - Once data is retrieved, it should be deserialized into the appropriate dataclasses from `entities.py`.
  - Future plans:
    - The plan is to support both synchronous and asynchronous clients, possibly with separate classes or a shared base class.
    - Add caching layer
    - Add convenience methods for common queries and data retrieval patterns, e.g. fetching all works by an author, retrieving references/citations, etc -- specifically designed for inexperienced users so they don't need to use the Client directly. For example, an UX like this:
        ```python
        from aletheca import Works

        works = Works.from_institution(name='University of City')
        journals = []
        for work in works:
            journals.extend(work.get_journals())
        ```
        note: this example is a complicated thing to do in the backend, as it involves multiple API calls, pagination, rate limiting, etc; plus openalex does not directly store the journal data so it needs some additional parsing/filtering -- but the idea is to make it easy for users to get started with common tasks without needing to understand all the API details.
        Also, this UX should be 'lazy' -- i.e. the data is only fetched when needed, not all at once upfront. This way, we can limit the amount of data transferred and processed, and avoid hitting rate limits unnecessarily. For this example above, we only need the 'locations' data from the works to get the journal info, so we should avoid fetching all the other data unless explicitly requested by the user. That means the `Works.from_institution` method should not actually do anything, but just construct a query object that can be iterated over to fetch the data as needed; which is then modified by the `work.get_journals()` call before actually making the API calls.

