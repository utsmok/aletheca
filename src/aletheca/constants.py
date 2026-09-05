"""Constants used throughout the Aletheca library."""

from importlib.metadata import PackageNotFoundError, version as _get_version

OPENALEX_API_BASE_URL = "https://api.openalex.org"

DEFAULT_TIMEOUT: int = 30
DEFAULT_RETRIES: int = 3
DEFAULT_PAGE_SIZE: int = 25

try:
    __version__: str = _get_version("aletheca")
except PackageNotFoundError:
    __version__: str = "0.0.0"

DEFAULT_USER_AGENT: str = f"aletheca/{__version__}"
CLIENT_HEADERS: dict[str, str] = {
    "accept": "application/json",
    "User-Agent": DEFAULT_USER_AGENT,
}
