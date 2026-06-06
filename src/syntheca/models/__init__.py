"""Pydantic models for OpenAlex entities."""

from .author import Author
from .award import Award
from .base import ApiResponse, BaseEntity, EntityType, Meta
from .common import (
    SDG,
    Affiliation,
    APCData,
    APCEntry,
    Biblio,
    CitationNormalizedPercentile,
    DehydratedFunder,
    DehydratedKeyword,
    DehydratedTopic,
    Domain,
    FieldEntity,
    Geo,
    HasContent,
    International,
    Location,
    Mesh,
    OpenAccess,
    Role,
    Society,
    Subfield,
    SummaryStats,
    TopicCount,
    TopicMinimal,
    TopicShare,
    YearCount,
    YearCountBasic,
)
from .dehydrated import (
    DehydratedAuthor,
    DehydratedConcept,
    DehydratedInstitution,
    DehydratedInstitutionWithYear,
    RelatedInstitution,
    SimpleDehydratedConcept,
)
from .funder import Funder
from .ids import (
    AuthorIds,
    ConceptIds,
    FunderIds,
    InstitutionIds,
    PublisherIds,
    SourceIds,
    TopicIds,
    WorkIds,
)
from .institution import Institution
from .keyword import Keyword
from .publisher import ParentPublisher, Publisher
from .safe_types import SafeList, SafeStr
from .source import Source
from .topic import Topic
from .work import Authorship, ContentUrls, DehydratedSource, Work

__all__ = [
    # Base
    "ApiResponse",
    "BaseEntity",
    "EntityType",
    "Meta",
    # Safe types
    "SafeList",
    "SafeStr",
    # Common nested
    "APCData",
    "APCEntry",
    "Affiliation",
    "Biblio",
    "CitationNormalizedPercentile",
    "DehydratedFunder",
    "DehydratedKeyword",
    "DehydratedTopic",
    "Domain",
    "FieldEntity",
    "Geo",
    "HasContent",
    "International",
    "Location",
    "Mesh",
    "OpenAccess",
    "Role",
    "SDG",
    "Society",
    "Subfield",
    "SummaryStats",
    "TopicCount",
    "TopicMinimal",
    "TopicShare",
    "YearCount",
    "YearCountBasic",
    # Dehydrated
    "DehydratedAuthor",
    "DehydratedConcept",
    "DehydratedInstitution",
    "DehydratedInstitutionWithYear",
    "RelatedInstitution",
    "SimpleDehydratedConcept",
    # IDs
    "AuthorIds",
    "ConceptIds",
    "FunderIds",
    "InstitutionIds",
    "PublisherIds",
    "SourceIds",
    "TopicIds",
    "WorkIds",
    # Entity models
    "Author",
    "Authorship",
    "Award",
    "ContentUrls",
    "DehydratedSource",
    "Funder",
    "Institution",
    "Keyword",
    "ParentPublisher",
    "Publisher",
    "Source",
    "Topic",
    "Work",
]
