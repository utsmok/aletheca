"""Client for the OpenAlex locations endpoint."""

from ..dialect import _OPENALEX_URL_PREFIX, OpenAlexResourceClient
from ..models import LocationRecord


class LocationsClient(OpenAlexResourceClient[LocationRecord]):
    """Client for the ``/locations`` endpoint.

    One row per copy of a work at one source (the per-copy index used for
    OA-copy hunting and repository-harvest audits). Rows are addressed by
    namespaced ids such as ``doi:10.7717/peerj.4375`` or
    ``pmh:oai:arXiv.org:1706.03762``; ``get``/``search``/``iterate`` behave
    like on the entity endpoints. A list request costs one credit.
    """

    path = "locations"
    model = LocationRecord

    def normalize_id(self, value: str) -> str:
        """Keep namespaced ids intact: the single route 404s on bare DOIs.

        Only URL and route prefixes are stripped; the ``doi:``/``pmh:``/
        ``pmid:`` namespace and the value's case stay as given.
        """
        text = value.strip()
        text = text.removeprefix(_OPENALEX_URL_PREFIX)
        return text.removeprefix(f"{self.path}/")
