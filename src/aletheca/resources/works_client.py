"""Client for the OpenAlex Works endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    SearchableMixin,
)
from pydantic import BaseModel

from ..models import ApiResponse, Work
from ..resources._standard import AlethecaResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class WorksClient(SearchableMixin, CursorIterableMixin, AlethecaResourceClient):
    """Client for the OpenAlex Works API endpoint.

    Supports GET by ID (including DOI/PMID), search, cursor iteration,
    full-text search, filtering, and sorting.
    """

    _entity_path: str = "works"
    # Widened annotations (ty 0.0.104+): a narrow override of a mutable base
    # attribute is rejected, but the value stays the per-endpoint model.
    _entity_model: type[BaseModel] | None = Work
    _search_response_model: type[BaseModel] | None = ApiResponse[Work]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "doi": "doi",
        "openalex_id": "openalex",
        "pmid": "pmid",
        "pmcid": "pmcid",
        "mag": "mag",
    }
    #: ``include_parts`` and ``corpus`` are works query parameters, not
    #: ``filter=`` keys; ``_serialize_filters`` emits them standalone.
    _standalone_params: frozenset[str] = frozenset({"include_parts", "corpus"})

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
        logger.debug("WorksClient initialized.")
