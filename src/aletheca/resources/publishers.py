"""Client for the OpenAlex publishers endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Publisher


class PublishersClient(OpenAlexResourceClient[Publisher]):
    """Client for the ``/publishers`` endpoint."""

    path = "publishers"
    model = Publisher
