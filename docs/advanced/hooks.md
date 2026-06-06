# Hooks

Aletheca supports request/response hooks through bibliofabric's hook system. Hooks
are callables invoked at specific points in the request lifecycle, allowing you to
add custom logging, metrics, header injection, parameter modification, or response
inspection without subclassing the client.

## Hook Types

### Pre-Request Hooks

Called **before** each HTTP request is sent. Hooks can modify query parameters and
headers in place.

```python
from collections.abc import Callable
from typing import Any

PreRequestHook = Callable[[str, str, dict[str, Any] | None, httpx.Headers], None]
```

**Parameters:**

| Parameter | Type | Mutable | Description |
|-----------|------|---------|-------------|
| `method` | `str` | No | HTTP method (`"GET"`, `"POST"`, etc.) |
| `url` | `str` | No | Full request URL |
| `params` | `dict[str, Any] \| None` | **Yes** | Query parameters — modify in place |
| `headers` | `httpx.Headers` | **Yes** | Request headers — modify in place |

### Post-Request Hooks

Called **after** a response is received and parsed. Hooks receive the raw response,
the parsed model (if any), and the number of attempts.

```python
PostRequestHook = Callable[[httpx.Response, Any, int], None]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `response` | `httpx.Response` | The raw HTTP response |
| `parsed_model` | `Any` | Parsed Pydantic model, or `None` if parsing failed |
| `attempts` | `int` | Number of request attempts made (always `1` for single requests) |

## Registering Hooks

Hooks are configured through `AlethecaSettings`:

```python
from aletheca import AlethecaSession
from aletheca.config import AlethecaSettings

def log_request(method, url, params, headers):
    print(f"→ {method} {url} params={params}")

def log_response(response, parsed_model, attempts):
    print(f"← {response.status_code} (attempts: {attempts})")

settings = AlethecaSettings(
    pre_request_hooks=[log_request],
    post_request_hooks=[log_response],
)

async with AlethecaSession(settings=settings) as session:
    work = await session.works.get("W2741809807")
```

## Examples

### Custom Request Logger

```python
import time

class RequestTimer:
    """Measure and log request durations via pre/post hooks."""

    def __init__(self):
        self._start_times: dict[str, float] = {}

    def before(self, method, url, params, headers):
        self._start_times[url] = time.monotonic()

    def after(self, response, parsed_model, attempts):
        url = str(response.url)
        elapsed = time.monotonic() - self._start_times.pop(url, 0)
        print(f"{response.status_code} {url} — {elapsed:.3f}s ({attempts} attempts)")

timer = RequestTimer()

settings = AlethecaSettings(
    pre_request_hooks=[timer.before],
    post_request_hooks=[timer.after],
)

async with AlethecaSession(settings=settings) as session:
    work = await session.works.get("W2741809807")
```

### Add Custom Headers

```python
def add_correlation_id(method, url, params, headers):
    import uuid
    headers["X-Correlation-ID"] = str(uuid.uuid4())

settings = AlethecaSettings(
    pre_request_hooks=[add_correlation_id],
)
```

### Response Metrics

```python
class MetricsCollector:
    """Collect response status code counts."""

    def __init__(self):
        self.status_codes: dict[int, int] = {}

    def record(self, response, parsed_model, attempts):
        code = response.status_code
        self.status_codes[code] = self.status_codes.get(code, 0) + 1

metrics = MetricsCollector()
settings = AlethecaSettings(post_request_hooks=[metrics.record])

async with AlethecaSession(settings=settings) as session:
    # ... make requests ...
    pass

print(metrics.status_codes)  # e.g., {200: 150, 429: 2}
```

## Error Handling in Hooks

Hook errors are caught and logged — they do **not** abort the request. If a hook
raises an exception, the error is logged at `ERROR` level and processing continues
with the next hook or the request itself.

```python
def flaky_hook(method, url, params, headers):
    raise RuntimeError("This hook fails but doesn't break the request")

# This is safe — the request still completes
settings = AlethecaSettings(pre_request_hooks=[flaky_hook])
```
