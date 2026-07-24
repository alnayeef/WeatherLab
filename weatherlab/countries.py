"""Resolve a user-typed country name into whatever each data source
actually expects, so that logic lives in exactly one place."""

from dataclasses import dataclass

import pycountry


@dataclass
class Country:
    iso3: str         # what OSCAR's territoryName parameter wants
    ogimet_name: str  # what Ogimet's state parameter wants


def resolve_country(name):
    """Raises LookupError if nothing matches."""
    match = pycountry.countries.search_fuzzy(name)[0]
    return Country(iso3=match.alpha_3, ogimet_name=match.name)
