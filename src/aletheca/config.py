"""
aletheca.config

configuration classes and settings for the Aletheca library, defining default parameters, API settings, user preferences, ...
"""

from dataclasses import dataclass

# TODO set up loguru here in the config module
# from loguru import logger
# ...


class OpenAlexAPISettings:
    """Configure API-based settings, like enabling xpac, data-v1, etc."""

    enable_xpac: bool = True  # https://docs.openalex.org/how-to-use-the-api/xpac
    enable_data_v1: bool = False


@dataclass
class BaseAlethecaConfig:
    """Base configuration class for Aletheca, holding the default settings, constants, preferences, ..."""

    api_base_url: str = "https://api.openalex.org"
    default_timeout: int = 10  # seconds
    max_retries: int = 3
    backoff_factor: float = 0.3
    user_agent: str = "AlethecaClient/0.1.0"
    email: str = ""
    rate_limit: int = 10  # requests per second
