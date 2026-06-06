"""Client for the OpenAlex Works endpoint."""

from typing import TYPE_CHECKING

from bibliofabric.log_config import logger
from bibliofabric.resources import (
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)

from ..models import ApiResponse, Work
from ..resources._standard import SynthecaResourceClient

if TYPE_CHECKING:
    from ..client import SynthecaClient


class WorksClient(
    GettableMixin, SearchableMixin, CursorIterableMixin, SynthecaResourceClient
):
    """Client for the OpenAlex Works API endpoint.

    Supports GET by ID (including DOI/PMID), search, cursor iteration,
    full-text search, filtering, and sorting.
    """

    _entity_path: str = "works"
    _entity_model: type[Work] = Work
    _search_response_model: type = ApiResponse[Work]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "SynthecaClient"):
        super().__init__(api_client)
        logger.debug("WorksClient initialized.")
