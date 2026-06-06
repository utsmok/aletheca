# API Reference

Auto-generated API documentation for aletheca's public modules.

## Session

::: aletheca.session.AlethecaSession
    options:
      heading_level: 2
      show_source: false
      members:
        - __init__
        - queries
        - close

## Client

::: aletheca.client.AlethecaClient
    options:
      heading_level: 2
      show_source: false
      members:
        - __init__
        - works
        - authors
        - sources
        - institutions
        - topics
        - keywords
        - publishers
        - funders

## Configuration

::: aletheca.config.AlethecaSettings
    options:
      heading_level: 2
      show_source: false

## Endpoint Filters

::: aletheca.endpoints.WorksFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.AuthorsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.SourcesFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.InstitutionsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.TopicsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.KeywordsFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.PublishersFilters
    options:
      heading_level: 3
      show_source: false

::: aletheca.endpoints.FundersFilters
    options:
      heading_level: 3
      show_source: false

## Resource Clients

::: aletheca.resources.WorksClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.AuthorsClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.SourcesClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.InstitutionsClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.TopicsClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.KeywordsClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.PublishersClient
    options:
      heading_level: 3
      show_source: false

::: aletheca.resources.FundersClient
    options:
      heading_level: 3
      show_source: false

## Convenience Queries

::: aletheca.queries
    options:
      heading_level: 2
      show_source: false
      members:
        - works_by_author
        - works_by_institution
        - works_by_doi
        - citing_works
        - referenced_works

## Helpers

::: aletheca._helpers
    options:
      heading_level: 2
      show_source: false
      members:
        - normalize_doi
        - parse_openalex_id
        - detect_id_type
        - reconstruct_abstract

## Models

::: aletheca.models.work.Work
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.author.Author
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.source.Source
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.institution.Institution
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.topic.Topic
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.keyword.Keyword
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.publisher.Publisher
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.funder.Funder
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.base.ApiResponse
    options:
      heading_level: 3
      show_source: false

::: aletheca.models.base.BaseEntity
    options:
      heading_level: 3
      show_source: false
