# Errors, retries, and rate limits

Every error inherits from `BibliofabricError` (re-exported from `aletheca`), and carries the failed `httpx.Request` and, when available, the `httpx.Response`.

```
BibliofabricError
├── APIError                     # any other 4xx/5xx; body holds the parsed JSON
│   ├── NotFoundError            # 404
│   └── RateLimitError           # 429
├── AuthError                    # 401 and 403
├── NetworkError                 # DNS, connection refused, reset
├── TimeoutError                 # also a builtin TimeoutError
├── ConfigurationError           # bad input caught client-side
└── ValidationError              # a record failed model validation
```

Catch specific types where you can react, and `BibliofabricError` as a last resort:

```python
from aletheca import NotFoundError, RateLimitError

try:
    work = await client.works.get("W0000000000")
except NotFoundError:
    ...
except RateLimitError as e:
    print(e.body)  # parsed JSON error payload, or None
```

Error strings redact credential query parameters, so printing them never leaks your key.

## Client-side guards

Some mistakes fail before any request is sent, with a `ConfigurationError`:

- More than 100 pipe-joined values in one filter.
- A `corpus` value outside `core`/`expansion`/`all` on `works.search()`.
- A `sample()` size outside 1 to 10,000.
- An unknown `search_scoped()` scope.

A record that fails model validation raises `ValidationError` with the raw payload (`raw`), the pydantic error (`error`), and the model name (`model_name`). In `iterate()` and `collect()`, pass `on_error="skip"` to drop bad records and collect them in a `failures` list instead.

## Retries

The client retries 429, 500, 502, 503, and 504 responses plus network errors and timeouts. A `Retry-After` header is honored when present; otherwise it waits with jittered exponential backoff, capped at `ALETHECA_MAX_RETRY_WAIT` (default 60 seconds). The number of attempts is `ALETHECA_MAX_RETRIES` (default 3).

One OpenAlex-specific veto: a 429 whose body carries `reason: "daily_budget"` is not retried, because it cannot succeed before the UTC midnight reset and retrying would only burn budget.

## Rate limits and budgets

OpenAlex meters requests in dollars per day, not requests per day. There is no polite pool: `mailto` is ignored.

| Access | Daily budget | Cursor paging |
|---|---|---|
| No key | $0.10/day per IP | First page only |
| Free key | $1/day | Full cursor paging |

Request types cost differently: plain list requests are cheapest, free-text search costs more (about 10x), and semantic search has its own per-second cap of 1 request. Content downloads cost the most.

Check your remaining budget for free:

```python
status = await live_or_keyed_client.rate_limit()
print(status.rate_limit.daily_remaining_usd)
```

`rate_limit()` reads the key from settings and never stores the echoed key value.

## Client-side pacing

Aletheca spaces requests to a default of 10 per second with at most 5 concurrent requests. Change both with `ALETHECA_MAX_REQUESTS_PER_SECOND` and `ALETHECA_MAX_CONCURRENCY`.

## Keyless 401s

The most common 401 is cursor paging without a key. Aletheca replaces the opaque upstream body with an `AuthError` that names the fix: get a free key and set `ALETHECA_API_KEY` (or pass `api_key=` to `AlethecaClient`). A keyed client keeps the upstream message.
