"""Syntheca: Python interface for the OpenAlex API."""

try:
    from importlib.metadata import PackageNotFoundError, version as _get_version

    __version__ = _get_version("syntheca")
except PackageNotFoundError:
    __version__ = "0.0.0"
