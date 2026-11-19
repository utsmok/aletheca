"""Client for the OpenAlex funders endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Funder


class FundersClient(OpenAlexResourceClient[Funder]):
    """Client for the ``/funders`` endpoint."""

    path = "funders"
    model = Funder
