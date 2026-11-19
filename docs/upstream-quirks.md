# Upstream quirks

Findings from verifying the live OpenAlex API against its OpenAPI spec and documentation in June 2026. Where a mismatch affects Aletheca, the workaround is noted. All reproduction URLs worked without an API key at the time.

## The OpenAPI spec is stale; the live API is ground truth

Across all nine entity endpoints, the live API returns 50+ fields that the [spec](https://developers.openalex.org/api-reference/openapi.json) does not model, and models 3 fields that the live API does not return (`longest_name` and `parsed_longest_name` on authors, `content_url` on works).

Highlights per entity:

| Entity | Live fields missing from spec | Spec fields absent from live API |
|---|---|---|
| Works | `apc_list`, `apc_paid`, `concepts`, `content_urls`, `corresponding_author_ids`, `corresponding_institution_ids`, `countries_distinct_count`, `has_fulltext`, `institutions`, `institutions_distinct_count`, `is_xpac`, `locations_count` | `content_url` |
| Authors | `block_key`, `full_name`, `raw_author_names`, `topic_share`, `x_concepts` | `longest_name`, `parsed_longest_name` |
| Sources | `alternate_titles`, `apc_prices`, `country_code`, `first_publication_year`, `is_core`, `is_high_oa_rate`, `is_high_oa_rate_since_year`, `is_in_doaj_since_year`, `is_in_scielo`, `is_ojs`, `last_publication_year`, `oa_flip_year`, `oa_works_count`, `societies`, `topic_share`, `topics` | — |
| Institutions | `associated_institutions`, `international`, `is_super_system`, `repositories`, `roles`, `status`, `topic_share`, `topics`, `type_id` | — |
| Topics | `siblings` | — |
| Publishers | `homepage_url`, `image_thumbnail_url`, `image_url`, `roles`, `summary_stats` | — |
| Funders | `awards_count`, `roles`, `summary_stats` | `grants_count`, `works_api_url` |
| Awards | `institution_awarded`, `primary_topic`, `topics` | — |

Two spec errors are more than omissions:

- `content_url` in the spec is a nullable string; the live API returns `content_urls`, an object with `pdf` and `grobid_xml` keys. Wrong name and wrong type. Aletheca models `Work.content_urls` as an object.
- The funder spec still says `grants_count`; the live API returns `awards_count`. Aletheca models `Funder.awards_count`.

Aletheca's models use `extra="allow"` everywhere, so fields that are missing from the spec and from the models still survive parsing.

## Documentation gaps

- `per_page` was documented as capped at 100 while 200 still worked. The August 2026 documentation update now documents 100 as the supported maximum; 200 is deprecated legacy behavior slated for removal. Aletheca caps at 100.
- The `llms.txt` endpoint list omits `/awards`, although the endpoint serves ~14.7M records with full spec coverage.
- `institution_awarded` on awards is returned on every record but appears in neither the spec nor the docs pages.
- The awards filter table lists about 23 filters while the API accepts 38+. The undocumented ones include `institution_awarded.continent`, `.country_code`, `.id`, `.lineage`, `.ror`, `.type`; `lead_investigator.affiliation.country`, `.affiliation.name`, `.family_name`, `.given_name`, `.orcid`; and `primary_topic.domain.id`, `.field.id`, `.id`, `.subfield.id` (and the same `topics.*` set). Send an invalid filter and read the 400 body to get the full list; `AwardsFilters` covers them.

## Live behaviors worth knowing

- `institution_awarded` is always a list, sometimes empty, despite the singular name. Each element has `id`, `display_name`, `ror`, `country_code`, `type`, `lineage`.
- `funded_outputs` on awards returns raw OpenAlex work URLs as strings, while sibling relationships such as `funder` return structured objects.
- Source `ids` no longer include a `fatcat` key. The removal was undocumented.
- Filter names and entity field names often differ (`best_oa_location` field vs `best_open_version` filter; `open_access.is_oa` field vs top-level `is_oa` filter). The filter models encode the filter names, not the field names.
- The polite pool is gone: since February 2026 OpenAlex ignores `mailto` and meters unkeyed traffic at $0.10/day per IP. See [errors, retries, and rate limits](errors.md).
- The API has no version in its base URL and no changelog; breaking changes (field renames, removals) happen silently. Trust the live API over any static schema.
