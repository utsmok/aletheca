"""Client for the OpenAlex keywords endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Keyword


class KeywordsClient(OpenAlexResourceClient[Keyword]):
    """Client for the ``/keywords`` endpoint."""

    path = "keywords"
    model = Keyword
