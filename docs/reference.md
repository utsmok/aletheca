# API reference

Generated from the source with mkdocstrings.

## Client

::: aletheca.AlethecaClient
    options:
      heading_level: 3
      show_source: false
      members:
        - works
        - authors
        - sources
        - institutions
        - topics
        - keywords
        - publishers
        - funders
        - awards
        - locations
        - links
        - autocomplete
        - rate_limit
        - request
        - is_retryable

## Settings

::: aletheca.AlethecaSettings
    options:
      heading_level: 3
      show_source: false

## Resource clients

Each resource client inherits the generic operations from
`bibliofabric.resources.ResourceClient` (`get`, `search`, `iterate`,
`collect`, `first`, `count`, `batch_get`) through
`aletheca.dialect.OpenAlexResourceClient`. Only class-specific members are
shown here.

::: aletheca.resources.works.WorksClient
    options:
      heading_level: 3
      show_source: false
      members:
        - search
        - search_scoped
        - sample
        - group_by
        - batch_get_by_doi
        - batch_get_by_openalex_id
        - citing
        - referenced
        - oa_pdf_urls

::: aletheca.resources.authors.AuthorsClient
    options:
      heading_level: 3
      show_source: false
      members:
        - batch_get_by_openalex_id

::: aletheca.resources.locations.LocationsClient
    options:
      heading_level: 3
      show_source: false
      members:
        - normalize_id

::: aletheca.resources.links.LinksClient
    options:
      heading_level: 3
      show_source: false
      members:
        - origin
        - target

## Filter models

Every filter model dumps with `by_alias=True` into OpenAlex dot-notation
keys and allows extra fields.

::: aletheca.filters.WorksFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.AuthorsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.SourcesFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.InstitutionsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.TopicsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.KeywordsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.PublishersFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.FundersFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.filters.AwardsFilters
    options:
      heading_level: 3
      show_source: false

## Dialect and helpers

::: aletheca.dialect
    options:
      heading_level: 3
      show_source: false
      members:
        - OPENALEX_API_BASE_URL
        - MAX_OR_VALUES
        - OpenAlexResourceClient

::: aletheca._helpers.reconstruct_abstract
    options:
      heading_level: 3
      show_source: false

## Models

Entity models live in `aletheca.models` and re-export from the top-level
package (`from aletheca import Work, Author, ...`). They are plain Pydantic
models; see the source for the full field list.

::: aletheca.models.Work
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.GroupByBucket
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.AutocompleteResult
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.RateLimitStatus
    options:
      heading_level: 3
      show_source: false
