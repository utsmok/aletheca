"""Client for the OpenAlex topics endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Topic


class TopicsClient(OpenAlexResourceClient[Topic]):
    """Client for the ``/topics`` endpoint."""

    path = "topics"
    model = Topic
