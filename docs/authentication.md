# Authentication

The OpenAlex API is free and open. Authentication is optional but recommended for better performance.

## Polite pool vs API key

OpenAlex operates two request pools:

| Pool | Speed | Requirements |
|---|---|---|
| **Polite pool** | Slower | No authentication needed |
| **API key pool** | Faster | Free API key from OpenAlex |

!!! tip
    The polite pool is rate-limited. For batch processing or scripts that make many requests, use an API key. You can request one at [https://openalex.org/signup](https://openalex.org/signup).

## Using an API key

### Environment variable (recommended)

Set the `SYNTHECA_OPENALEX_API_KEY` environment variable. Syntheca reads it automatically via its settings system:

```bash
export SYNTHECA_OPENALEX_API_KEY="your-api-key-here"
```

Then create a session as usual — no extra code needed:

```python
from syntheca import SynthecaSession

async with SynthecaSession() as session:
    work = await session.works.get("W2741809807")
```

### .env file

Syntheca loads `.env` and `secrets.env` files automatically (via pydantic-settings). Create a `.env` file in your project root:

```
SYNTHECA_OPENALEX_API_KEY=your-api-key-here
```

!!! warning "Don't commit secrets"
    Add `.env` and `secrets.env` to your `.gitignore`. Never commit API keys to version control.

### Explicit parameter

Pass the key directly to the session constructor:

```python
from syntheca import SynthecaSession

async with SynthecaSession(api_key="your-api-key-here") as session:
    work = await session.works.get("W2741809807")
```

### Via SynthecaSettings

For advanced configuration, construct a settings object:

```python
from syntheca import SynthecaSession
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(openalex_api_key="your-api-key-here")

async with SynthecaSession(settings=settings) as session:
    ...
```

## How it works

When an API key is provided, syntheca appends it as the `api_key` query parameter on every request:

```
https://api.openalex.org/works?filter=...&api_key=your-key
```

When no key is set, requests are made without authentication and go through the polite pool.

??? note "Custom base URL"
    If you override `base_url`, the API key parameter is still appended to all requests. This is useful for testing against a proxy or mock server.
