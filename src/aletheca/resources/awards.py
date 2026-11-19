"""Client for the OpenAlex awards endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Award


class AwardsClient(OpenAlexResourceClient[Award]):
    """Client for the ``/awards`` endpoint."""

    path = "awards"
    model = Award
