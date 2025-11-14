"""
aletheca.utils
utility functions used in aletheca
split into several groups:
    - parsing/normalizing of various parameters and fields?
    - polars df standard methods?
    - ...
"""


# --------
# Parse and normalize functions
# --------


def normalize_doi(doi: str) -> str:
    # normalize doi to canonical form: https://doi.org/10.xxxx/xxxxx, all lowercase
    ...


def short_doi(doi: str) -> str:
    # convert full doi url to short form: 10.xxxx/xxxxx
    ...


def determine_id_type(id_str: str) -> str:
    # determines the type of identifier string, e.g. doi, openalex_id, orcid, ror, etc
    ...


def parse_inverted_abstract(inv_abstract: dict[int, str]) -> str:
    # parse inverted abstract dict to normal abstract string
    ...


# --------
# Polars dataframe utility functions
# --------
