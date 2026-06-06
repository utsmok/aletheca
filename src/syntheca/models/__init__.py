"""Pydantic models for OpenAlex entities."""

from .base import ApiResponse, BaseEntity, EntityType, Meta
from .common import (
    APCData,
    APCEntry,
    Affiliation,
    Biblio,
    CitationNormalizedPercentile,
    DehydratedFunder,
    DehydratedKeyword,
    DehydratedTopic,
    Domain,
    FieldEntity,
    Geo,
    Grant,
    HasContent,
    International,
    Location,
    Mesh,
    OpenAccess,
    Role,
    SDG,
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
from .author import Author
from .award import Award
from .funder import Funder
from .institution import Institution
from .keyword import Keyword
from .publisher import Publisher
from .safe_types import SafeList, SafeStr
from .source import Source
from .topic import Topic
from .work import Authorship, DehydratedSource, Work

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
    "Grant",
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
    "DehydratedSource",
    "Funder",
    "Institution",
    "Keyword",
    "Publisher",
    "Source",
    "Topic",
    "Work",
]
