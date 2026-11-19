# Authentication

The OpenAlex API is free and open. Authentication is optional but recommended for better performance.

## API keys

The polite pool no longer exists: since February 2026 OpenAlex ignores `mailto`
and meters unkeyed traffic at $0.10/day per IP address. A free API key raises
the budget to $1/day, enables cursor paging past the first page, and is
required for deep iteration. Request one at
[https://openalex.org/settings/api](https://openalex.org/settings/api).

## Using an API key

### Environment variable (recommended)

Set the `ALETHECA_OPENALEX_API_KEY` environment variable. Aletheca reads it automatically via its settings system:

```bash
export ALETHECA_API_KEY="your-api-key-here"
```

Then create a session as usual — no extra code needed:

```python
from aletheca import AlethecaSession

async with AlethecaSession() as session:
    work = await session.works.get("W2741809807")
```

### .env file

Aletheca loads `.env` and `secrets.env` files automatically (via pydantic-settings). Create a `.env` file in your project root:

```
ALETHECA_OPENALEX_API_KEY=your-api-key-here
```

!!! warning "Don't commit secrets"
    Add `.env` and `secrets.env` to your `.gitignore`. Never commit API keys to version control.

### Explicit parameter

Pass the key directly to the session constructor:

```python
from aletheca import AlethecaSession

async with AlethecaSession(api_key="your-api-key-here") as session:
    work = await session.works.get("W2741809807")
```

### Via AlethecaSettings

For advanced configuration, construct a settings object:

```python
from aletheca import AlethecaSession
from aletheca.config import AlethecaSettings

settings = AlethecaSettings(openalex_api_key="your-api-key-here")

async with AlethecaSession(settings=settings) as session:
    ...
```

## How it works

When an API key is provided, aletheca appends it as the `api_key` query parameter on every request:

```
https://api.openalex.org/works?filter=...&api_key=your-key
```

When no key is set, requests share OpenAlex's small unkeyed budget ($0.10/day per IP address) and cursor paging stops after the first page with a 401; set a free API key for real harvesting.

??? note "Custom base URL"
    If you override `base_url`, the API key parameter is still appended to all requests. This is useful for testing against a proxy or mock server.
