# Rate Limiting

OpenAlex applies rate limits to API requests. Syntheca provides automatic rate limit
handling through bibliofabric's built-in rate limiting, including proactive throttling,
`Retry-After` header parsing, and exponential backoff on 429 responses.

## OpenAlex Rate Limits

| Tier | Rate Limit | Notes |
|------|-----------|-------|
| **No key (polite pool)** | ~10 requests/second | Requires `mailto` parameter or User-Agent with contact info |
| **API key** | Higher throughput | Request at [openalex.org](https://openalex.org) |

Without an API key, you are in the "polite pool." The polite pool provides lower
priority and slower response times. Adding an API key moves you to a faster pool.

## Configuring Your API Key

### Environment Variable (Recommended)

```bash
export SYNTHECA_OPENALEX_API_KEY="your-api-key-here"
```

### `.env` File

```env
SYNTHECA_OPENALEX_API_KEY=your-api-key-here
```

### Programmatic

```python
from syntheca import SynthecaSession

async with SynthecaSession(api_key="your-api-key-here") as session:
    ...
```

The API key is sent as a `?api_key=` query parameter on every request.

## How Syntheca Handles Rate Limiting

### 1. Proactive Throttling

When `enable_rate_limiting=True` (default), the client reads rate limit headers
from every response:

- `X-RateLimit-Limit` — total requests allowed in the window
- `X-RateLimit-Remaining` — remaining requests in the window
- `X-RateLimit-Reset` — timestamp when the window resets

If `remaining` falls below the buffer threshold (`rate_limit_buffer_percentage`, default 10%),
the client automatically waits until the reset time before sending the next request.

```python
from syntheca import SynthecaSession
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(
    enable_rate_limiting=True,
    rate_limit_buffer_percentage=0.15,  # Start waiting at 15% remaining
)
```

### 2. Reactive Handling (429 Responses)

If the API returns a 429 (Too Many Requests):

1. The client raises a `RateLimitError`.
2. The retry mechanism catches it and waits based on the `Retry-After` header.
3. If no `Retry-After` header is present, it waits `rate_limit_retry_after_default`
   seconds (default: 60).
4. The request is retried up to `max_retries` times with exponential backoff.

### 3. Retry with Exponential Backoff

Retries use `tenacity` with configurable exponential backoff:

```python
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(
    max_retries=5,
    backoff_factor=1.0,  # Wait 1s, 2s, 4s, 8s, 16s between retries
    rate_limit_retry_after_default=30,  # Wait 30s if no Retry-After header
)
```

Retryable status codes: `429`, `500`, `502`, `503`, `504`.

### Disabling Rate Limiting

```python
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(enable_rate_limiting=False)
```

!!! warning
    Disabling rate limiting means the client will not proactively throttle or
    respect `Retry-After` headers. You are responsible for staying within limits.

## Best Practices

1. **Always use an API key** in production. It provides faster response times and
   higher throughput.
2. **Use cursor pagination** (`iterate`) instead of page-based pagination — it's
   more efficient and reduces request count.
3. **Set `per_page=200`** (the maximum) for iteration to minimize requests.
4. **Increase `max_retries`** for batch jobs that may encounter transient rate limits.
5. **Add `backoff_factor`** proportional to your concurrency level.
