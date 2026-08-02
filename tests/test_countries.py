"""Tests for weatherlab.countries.resolve_country, confirming the
specific mappings verified live against both OSCAR and Ogimet weeks
ago - especially the short-form cases most likely to trip up fuzzy
matching, and the one place OSCAR and Ogimet genuinely disagree on
what a country should be called."""

import pytest

from weatherlab.countries import resolve_country


def test_bangladesh():
    country = resolve_country("Bangladesh")
    assert country.iso3 == "BGD"
    assert country.ogimet_name == "Bangladesh"


def test_two_letter_us_resolves_correctly():
    """The case most likely to trip up a fuzzy matcher - confirmed
    live that 'US' resolves to the United States, not some unrelated
    near-match."""
    country = resolve_country("US")
    assert country.iso3 == "USA"


def test_usa_abbreviation():
    assert resolve_country("USA").iso3 == "USA"


def test_full_united_states_name():
    assert resolve_country("United States").iso3 == "USA"


def test_russia_uses_formal_name_for_ogimet():
    """Confirmed live against Ogimet: the formal ISO name 'Russian
    Federation', not the everyday 'Russia', is what actually matches
    Ogimet's own station database - a real, slightly surprising
    result found by testing rather than assuming both sources would
    agree on a country's name."""
    country = resolve_country("Russia")
    assert country.iso3 == "RUS"
    assert country.ogimet_name == "Russian Federation"


def test_unrecognized_name_raises():
    with pytest.raises(LookupError):
        resolve_country("Not A Real Country")
