"""Pydantic models for OpenAlex entities."""

from bibliofabric import SafeList, SafeStr

from .author import Author
from .award import (
    Award,
    AwardFunder,
    AwardInvestigator,
    InvestigatorAffiliation,
    LinkedAward,
    Recipient,
    RecipientCountry,
    ResearchScope,
)
from .base import ApiResponse, BaseEntity, Meta
from .common import (
    SDG,
    Affiliation,
    APCData,
    APCEntry,
    APCYear,
    Biblio,
    CitationNormalizedPercentile,
    CitedByPercentileYear,
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
    DehydratedSource,
    RelatedInstitution,
    RelatedWork,
    SimpleDehydratedConcept,
)
from .funder import Funder
from .ids import (
    AuthorIds,
    ConceptIds,
    FunderIds,
    InstitutionIds,
    KeywordIds,
    PublisherIds,
    SourceIds,
    TopicIds,
    WorkIds,
)
from .institution import Institution
from .keyword import Keyword
from .publisher import ParentPublisher, Publisher
from .source import Source
from .topic import Topic
from .work import Authorship, ContentUrls, StudyDesign, Work, WorkAward

__all__ = [
    # Base
    "ApiResponse",
    "BaseEntity",
    "Meta",
    # Safe types
    "SafeList",
    "SafeStr",
    # Common nested
    "APCData",
    "APCEntry",
    "APCYear",
    "Affiliation",
    "Biblio",
    "CitedByPercentileYear",
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
    "DehydratedSource",
    "RelatedInstitution",
    "RelatedWork",
    "SimpleDehydratedConcept",
    # IDs
    "AuthorIds",
    "ConceptIds",
    "FunderIds",
    "InstitutionIds",
    "KeywordIds",
    "PublisherIds",
    "SourceIds",
    "TopicIds",
    "WorkIds",
    # Entity models
    "Author",
    "Authorship",
    "Award",
    "AwardFunder",
    "AwardInvestigator",
    "ContentUrls",
    "Funder",
    "Institution",
    "InvestigatorAffiliation",
    "Keyword",
    "LinkedAward",
    "ParentPublisher",
    "Publisher",
    "Recipient",
    "RecipientCountry",
    "ResearchScope",
    "Source",
    "StudyDesign",
    "Topic",
    "Work",
    "WorkAward",
]
