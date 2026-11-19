# Links

`client.links` talks to the `/links` endpoint and returns `Link` models: typed one-hop edges between works, each labeled with a relationship URL (`https://openalex.org/relationships/citation` and the part-of relationships).

```python
references = await client.links.origin("W2741809807")  # edges leaving the work
citations = await client.links.target("W2741809807")  # edges pointing at it
```

`origin()` sends `filter=origin:<id>` and `target()` sends `filter=target:<id>`; both cursor-page up to `limit` (default 100) edges. Bare `W...` ids and full URLs normalize. Each `Link` exposes `origin`, `target`, and `relationship`. A list request costs one credit.

Use `client.links.search({"origin": "W..."})` or `iterate()` for raw queries beyond the two helpers.
