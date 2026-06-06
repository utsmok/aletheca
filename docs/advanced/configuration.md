# Configuration

Syntheca is built on [bibliofabric](https://github.com/nicholasgasior/bibliofabric) and inherits
its configuration system. Settings are managed through `SynthecaSettings`, a Pydantic
Settings model that loads values from environment variables, `.env` files, or programmatic
construction.

## SynthecaSettings

`SynthecaSettings` inherits all fields from bibliofabric's `BaseApiSettings` and adds
OpenAlex-specific options.

### All Settings Fields

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|-------------|-------------|
| **Client Behavior** | | | | |
| `request_timeout` | `float` | `30.0` | `SYNTHECA_REQUEST_TIMEOUT` | HTTP request timeout in seconds |
| `max_retries` | `int` | `3` | `SYNTHECA_MAX_RETRIES` | Maximum retry attempts for transient errors |
| `backoff_factor` | `float` | `0.5` | `SYNTHECA_BACKOFF_FACTOR` | Exponential backoff multiplier (seconds) |
| `user_agent` | `str` | `syntheca/<version>` | `SYNTHECA_USER_AGENT` | User-Agent header for HTTP requests |
| **OpenAlex-Specific** | | | | |
| `openalex_api_key` | `str \| None` | `None` | `SYNTHECA_OPENALEX_API_KEY` | OpenAlex API key for the polite pool |
| **Rate Limiting** | | | | |
| `enable_rate_limiting` | `bool` | `True` | `SYNTHECA_ENABLE_RATE_LIMITING` | Enable/disable automatic rate limit handling |
| `rate_limit_buffer_percentage` | `float` | `0.1` | `SYNTHECA_RATE_LIMIT_BUFFER_PERCENTAGE` | Buffer threshold (0.1 = 10%) before proactive throttling |
| `rate_limit_retry_after_default` | `int` | `60` | `SYNTHECA_RATE_LIMIT_RETRY_AFTER_DEFAULT` | Default wait time (seconds) if no `Retry-After` header on 429 |
| **Caching** | | | | |
| `enable_caching` | `bool` | `False` | `SYNTHECA_ENABLE_CACHING` | Enable client-side response caching |
| `cache_ttl_seconds` | `int` | `300` | `SYNTHECA_CACHE_TTL_SECONDS` | Time-to-live for cached responses (seconds) |
| `cache_max_size` | `int` | `128` | `SYNTHECA_CACHE_MAX_SIZE` | Maximum number of entries in the LRU cache |
| **Hooks** | | | | |
| `pre_request_hooks` | `list[PreRequestHook]` | `[]` | — | Callable hooks invoked before each request |
| `post_request_hooks` | `list[PostRequestHook]` | `[]` | — | Callable hooks invoked after each response |

## Environment Variable Prefix

All settings are prefixed with `SYNTHECA_`. The settings model uses `pydantic-settings`
with `env_prefix="SYNTHECA_"` and `case_sensitive=False`, so both `SYNTHECA_OPENALEX_API_KEY`
and `syntheca_openalex_api_key` work.

## Configuration Methods

### 1. Environment Variables

```bash
export SYNTHECA_OPENALEX_API_KEY="your-api-key"
export SYNTHECA_REQUEST_TIMEOUT="60"
export SYNTHECA_MAX_RETRIES="5"
export SYNTHECA_ENABLE_CACHING="true"
export SYNTHECA_CACHE_TTL_SECONDS="600"
```

### 2. `.env` File

Create a `.env` or `secrets.env` file in your project root:

```env
SYNTHECA_OPENALEX_API_KEY=your-api-key
SYNTHECA_REQUEST_TIMEOUT=60
SYNTHECA_MAX_RETRIES=5
```

Syntheca loads both `.env` and `secrets.env` automatically. The `secrets.env` file
is intended for sensitive values like API keys — add it to `.gitignore`.

### 3. Programmatic Configuration

Pass a `SynthecaSettings` instance to `SynthecaSession`:

```python
from syntheca import SynthecaSession
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(
    openalex_api_key="your-api-key",
    request_timeout=60.0,
    max_retries=5,
    enable_caching=True,
    cache_ttl_seconds=600,
    cache_max_size=256,
)

async with SynthecaSession(settings=settings) as session:
    work = await session.works.get("W2741809807")
```

### 4. Inline API Key

For quick usage, pass the API key directly:

```python
from syntheca import SynthecaSession

async with SynthecaSession(api_key="your-api-key") as session:
    async for work in session.works.iterate(
        filters=WorksFilters(publication_year=2024),
    ):
        print(work.display_name)
```

## Settings Caching

`get_settings()` uses `@lru_cache` — the settings instance is created once and reused.
If you need different settings for different sessions, construct `SynthecaSettings`
explicitly and pass it to the session constructor.

```python
from syntheca.config import SynthecaSettings

# These produce different instances
fast_settings = SynthecaSettings(request_timeout=10, max_retries=1)
robust_settings = SynthecaSettings(request_timeout=120, max_retries=10)

# Each session gets its own settings
async with SynthecaSession(settings=fast_settings) as fast_session:
    ...
async with SynthecaSession(settings=robust_settings) as robust_session:
    ...
```

## Base URL Override

To point at a different OpenAlex instance (e.g., a mirror or test server):

```python
from syntheca import SynthecaSession

async with SynthecaSession(base_url="https://custom-openalex.example.com") as session:
    ...
```
