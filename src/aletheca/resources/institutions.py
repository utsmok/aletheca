"""Client for the OpenAlex institutions endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Institution


class InstitutionsClient(OpenAlexResourceClient[Institution]):
    """Client for the ``/institutions`` endpoint."""

    path = "institutions"
    model = Institution
