"""Client for the OpenAlex sources endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Source


class SourcesClient(OpenAlexResourceClient[Source]):
    """Client for the ``/sources`` endpoint."""

    path = "sources"
    model = Source
