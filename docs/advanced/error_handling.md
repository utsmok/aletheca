# Error Handling

Aletheca uses bibliofabric's exception hierarchy for all errors. Every exception
inherits from `BibliofabricError`, allowing you to catch all library errors with
a single handler or target specific error types.

## Exception Hierarchy

```
BibliofabricError
├── APIError                    # Generic 4xx/5xx HTTP errors
│   ├── NotFoundError           # 404 Not Found
│   └── RateLimitError          # 429 Too Many Requests
├── ValidationError             # Invalid request parameters
├── TimeoutError                # Request exceeded timeout
├── NetworkError                # DNS failure, connection refused, etc.
├── ConfigurationError          # Misconfigured client settings
├── AuthError                   # Authentication failure
└── BibliofabricRequestError    # Other HTTP request errors
```

## Exception Reference

### BibliofabricError

The base exception for all library errors. Every exception carries:

- `message: str` — Human-readable error description.
- `response: httpx.Response | None` — The HTTP response, if available.
- `request: httpx.Request | None` — The HTTP request, if available.

```python
from bibliofabric.exceptions import BibliofabricError

try:
    work = await session.works.get("W_INVALID")
except BibliofabricError as e:
    print(e.message)
    print(e.response.status_code if e.response else "No response")
```

### APIError

Raised for non-specific HTTP error responses (4xx/5xx not covered by subtypes).

```python
from bibliofabric.exceptions import APIError

try:
    work = await session.works.get("W123")
except APIError as e:
    print(f"HTTP {e.response.status_code}: {e.message}")
```

### NotFoundError

Raised when the requested resource does not exist (HTTP 404).

```python
from bibliofabric.exceptions import NotFoundError

try:
    work = await session.works.get("W_NONEXISTENT")
except NotFoundError:
    print("Work not found")
```

### RateLimitError

Raised when the API rate limit is exceeded (HTTP 429). This is a **retryable** error —
the client's retry mechanism will catch it, wait based on `Retry-After` headers, and
retry automatically.

```python
from bibliofabric.exceptions import RateLimitError

try:
    async for work in session.works.iterate(filters=filters, per_page=200):
        process(work)
except RateLimitError as e:
    print(f"Rate limited even after retries: {e.message}")
```

### TimeoutError

Raised when a request exceeds the configured `request_timeout`.

```python
from bibliofabric.exceptions import TimeoutError

try:
    work = await session.works.get("W123")
except TimeoutError as e:
    print(f"Request timed out: {e.message}")
```

### NetworkError

Raised for connection-level failures: DNS resolution errors, connection refused,
network unreachable, etc.

```python
from bibliofabric.exceptions import NetworkError

try:
    work = await session.works.get("W123")
except NetworkError as e:
    print(f"Network failure: {e.message}")
```

### ValidationError

Raised for invalid request parameters or client-side validation failures.

### ConfigurationError

Raised when client settings are invalid or conflicting.

### AuthError

Raised when authentication fails (e.g., an auth strategy cannot obtain credentials).

## Retry Behavior

The client automatically retries on transient errors using `tenacity` with
exponential backoff.

### What Gets Retried

| Condition | Retryable |
|-----------|-----------|
| `TimeoutError` | ✅ Yes |
| `NetworkError` | ✅ Yes |
| `RateLimitError` (429) | ✅ Yes |
| `APIError` with status 500, 502, 503, 504 | ✅ Yes |
| `APIError` with status 400, 401, 403, 404 | ❌ No |
| `ValidationError` | ❌ No |
| `AuthError` | ❌ No |

### Retry Configuration

```python
from aletheca.config import AlethecaSettings

settings = AlethecaSettings(
    max_retries=5,          # Up to 5 retry attempts (6 total including initial)
    backoff_factor=1.0,     # Exponential backoff: 1s, 2s, 4s, 8s, 16s
)
```

The backoff formula is `backoff_factor * (2 ** attempt)`. With `backoff_factor=0.5`
(default), retries wait approximately 0.5s, 1s, 2s, 4s, 8s.

## Error Handling Patterns

### Catch-All Handler

```python
from bibliofabric.exceptions import BibliofabricError

async with AlethecaSession() as session:
    try:
        work = await session.works.get("W2741809807")
    except BibliofabricError as e:
        print(f"Something went wrong: {e}")
        if e.response:
            print(f"Status: {e.response.status_code}")
            print(f"Body: {e.response.text}")
```

### Granular Error Handling

```python
from bibliofabric.exceptions import (
    NotFoundError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    APIError,
    BibliofabricError,
)

async with AlethecaSession() as session:
    try:
        work = await session.works.get(work_id)
    except NotFoundError:
        print(f"Work {work_id} not found")
    except RateLimitError:
        print("Rate limit exceeded — consider adding an API key")
    except TimeoutError:
        print("Request timed out — try increasing request_timeout")
    except NetworkError:
        print("Network error — check your internet connection")
    except APIError as e:
        print(f"API error {e.response.status_code}: {e.message}")
    except BibliofabricError as e:
        print(f"Unexpected error: {e}")
```

### Retry-Resistant Batch Processing

For large batch jobs where individual failures should not stop the entire process:

```python
from bibliofabric.exceptions import (
    BibliofabricError,
    NotFoundError,
    RateLimitError,
)

async with AlethecaSession() as session:
    work_ids = ["W1", "W2", "W3", "W_INVALID", "W4"]

    for wid in work_ids:
        try:
            work = await session.works.get(wid)
            print(f"✓ {wid}: {work.display_name}")
        except NotFoundError:
            print(f"✗ {wid}: not found — skipping")
        except RateLimitError:
            print(f"✗ {wid}: rate limited after retries — stopping batch")
            break
        except BibliofabricError as e:
            print(f"✗ {wid}: {type(e).__name__}: {e.message}")
```
