# Locations

`client.locations` talks to the `/locations` endpoint and returns `LocationRecord` models. This is OpenAlex's per-copy index: one row per copy of a work at one source, useful for OA-copy hunting and repository-harvest audits.

```python
record = await client.locations.get("doi:10.7717/peerj.4375")

page = await client.locations.search({"doi": "10.7717/peerj.4375"})
```

Single rows are addressed by namespaced ids (`doi:...`, `pmh:...`, `pmid:...`, `mag:...`). The library keeps the namespace intact: a bare DOI 404s on this endpoint. List and search requests cost one credit.

Each row carries `work_id`, `native_id` and `native_id_namespace`, `provenance`, `title`, `type`, `language`, `is_oa`, `pdf_url`, `landing_page_url`, a typed `urls` list (`url`, `content_type`), a typed `ids` list (`id`, `namespace`, `relationship`), and the flattened `source_id`/`source_name`/`publisher`.

For "give me the PDF links for this work", prefer [works.oa_pdf_urls()](works.md#pdf-links): it fetches the work once and orders copies best OA first, without paying for a locations query.
