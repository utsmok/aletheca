# Caching

Syntheca supports client-side response caching via [cachetools'](https://github.com/tkem/cachetools)
`TTLCache` — an in-memory LRU (Least Recently Used) cache with time-to-live expiration.
Caching is disabled by default and applies only to `GET` requests with an `expected_model`.

## How It Works

When caching is enabled:

1. Before each `GET` request, the client generates a cache key from the HTTP method, URL,
   and query parameters (sorted for consistency).
2. If a cache hit is found and the cached value matches the expected Pydantic model type,
   the cached model is returned immediately — **no HTTP request is made**.
3. On cache miss, the request proceeds normally. Successful responses with a parsed model
   are stored in the cache.
4. Cache entries expire after `cache_ttl_seconds` or when `cache_max_size` entries are
   exceeded (LRU eviction).

## Enabling Caching

### Via Environment Variables

```bash
export SYNTHECA_ENABLE_CACHING="true"
export SYNTHECA_CACHE_TTL_SECONDS="600"
export SYNTHECA_CACHE_MAX_SIZE="256"
```

### Via Programmatic Configuration

```python
from syntheca import SynthecaSession
from syntheca.config import SynthecaSettings

settings = SynthecaSettings(
    enable_caching=True,
    cache_ttl_seconds=600,  # 10 minutes
    cache_max_size=256,      # Up to 256 unique requests cached
)

async with SynthecaSession(settings=settings) as session:
    # First call: HTTP request + cache store
    work1 = await session.works.get("W2741809807")
    # Second call: cache hit, no HTTP request
    work2 = await session.works.get("W2741809807")
    assert work1 is work2  # Same object from cache
```

## Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enable_caching` | `bool` | `False` | Master switch for caching |
| `cache_ttl_seconds` | `int` | `300` | Seconds before cached entries expire (5 minutes default) |
| `cache_max_size` | `int` | `128` | Maximum cached entries before LRU eviction |

## What Gets Cached

Only `GET` requests with an `expected_model` are cached. This means:

- **Cached:** `session.works.get(...)`, `session.works.iterate(...)`, `session.works.search(...)`
- **Not cached:** Raw requests without a model, `POST`/`PUT`/`DELETE` requests

The cache stores the **parsed Pydantic model**, not the raw HTTP response. This means
cache hits return fully validated model instances without reparsing.

## Cache Invalidation

The cache provides no explicit invalidation API. Entries expire through:

1. **TTL expiration** — after `cache_ttl_seconds` have elapsed.
2. **LRU eviction** — when the cache exceeds `cache_max_size`, the least recently used
   entry is removed.
3. **Session teardown** — the cache is an in-memory object attached to the client.
   When the session closes, the cache is discarded.

For workflows requiring fresh data, either:

- Set a short `cache_ttl_seconds` (e.g., `60`).
- Create a new `SynthecaSession` to get a fresh cache.
- Disable caching entirely.

## Performance Considerations

The cache key is an MD5 hash of the method, URL, and sorted query parameters. This
means identical filter combinations map to the same cache entry regardless of filter
construction order:

```python
# These produce the same cache key
filters1 = WorksFilters(publication_year=2024, is_oa=True)
filters2 = WorksFilters(is_oa=True, publication_year=2024)
```

For high-volume iteration workloads (cursor pagination), caching is typically not
beneficial because each cursor position produces a unique URL. Consider disabling
caching or using a very short TTL for iteration-heavy sessions.
