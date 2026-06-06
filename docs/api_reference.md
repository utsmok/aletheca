# API Reference

Auto-generated API documentation for syntheca's public modules.

## Session

::: syntheca.session.SynthecaSession
    options:
      heading_level: 2
      show_source: false
      members:
        - __init__
        - queries
        - close

## Client

::: syntheca.client.SynthecaClient
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

::: syntheca.config.SynthecaSettings
    options:
      heading_level: 2
      show_source: false

## Endpoint Filters

::: syntheca.endpoints.WorksFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.AuthorsFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.SourcesFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.InstitutionsFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.TopicsFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.KeywordsFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.PublishersFilters
    options:
      heading_level: 3
      show_source: false

::: syntheca.endpoints.FundersFilters
    options:
      heading_level: 3
      show_source: false

## Resource Clients

::: syntheca.resources.WorksClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.AuthorsClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.SourcesClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.InstitutionsClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.TopicsClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.KeywordsClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.PublishersClient
    options:
      heading_level: 3
      show_source: false

::: syntheca.resources.FundersClient
    options:
      heading_level: 3
      show_source: false

## Convenience Queries

::: syntheca.queries
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

::: syntheca._helpers
    options:
      heading_level: 2
      show_source: false
      members:
        - normalize_doi
        - parse_openalex_id
        - detect_id_type
        - reconstruct_abstract

## Models

::: syntheca.models.work.Work
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.author.Author
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.source.Source
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.institution.Institution
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.topic.Topic
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.keyword.Keyword
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.publisher.Publisher
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.funder.Funder
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.base.ApiResponse
    options:
      heading_level: 3
      show_source: false

::: syntheca.models.base.BaseEntity
    options:
      heading_level: 3
      show_source: false
