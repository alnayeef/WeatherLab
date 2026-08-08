"""Tests for weatherlab.regions."""

from weatherlab.countries import resolve_country
import pytest
from weatherlab.regions import countries_in_bbox, parse_bbox, resolve_bbox_countries


def test_small_box_inside_one_country():
    assert countries_in_bbox(89, 23, 91, 25) == ["BGD"]


def test_box_spanning_two_countries():
    codes = countries_in_bbox(88, 22, 90, 26)
    assert set(codes) == {"IND", "BGD"}


def test_western_europe_box_excludes_fiji():
    """Regression test: a naive bounding-box comparison (rather than
    real geometric intersection) would incorrectly include Fiji here
    - its islands straddle the antimeridian, making its naive
    min/max bounds span the entire globe's longitude range."""
    codes = countries_in_bbox(2, 45, 8, 50)
    assert "FJI" not in codes
    assert "DEU" in codes


def test_missing_iso_a3_falls_back_to_adm0_a3():
    """Regression test: Norway and France have no standard ISO_A3 in
    this dataset (Natural Earth uses '-99' as a placeholder) - a box
    over either must still resolve to a real code via ADM0_A3, not
    silently drop them or return the placeholder itself."""
    codes = countries_in_bbox(5, 58, 12, 62)  # southern Norway
    assert "NOR" in codes
    assert "-99" not in codes


def test_resolve_bbox_countries_returns_usable_names():
    names, skipped = resolve_bbox_countries(89, 23, 91, 25)
    assert names == ["Bangladesh"]
    assert skipped == []


def test_resolve_bbox_countries_names_round_trip_through_resolve_country():
    """The whole point of returning names rather than codes directly
    - confirms a name produced here resolves back to the exact same
    ISO3 code via resolve_country(), the same function surface_obs
    and StationDB already use for a single --country value."""
    names, _ = resolve_bbox_countries(88, 22, 90, 26)
    for name in names:
        country = resolve_country(name)
        assert country.iso3 in {"IND", "BGD"}


def test_resolve_bbox_countries_skips_unresolvable_disputed_territory():
    """Regression test: confirmed live that Kosovo's Natural Earth
    code (KOS) has no pycountry entry at all, so there's no reliable
    way to fetch OSCAR/Ogimet data for it under this project's
    country-name architecture - it must be reported as skipped, not
    silently dropped or allowed to crash the whole lookup."""
    names, skipped = resolve_bbox_countries(20.0, 41.8, 21.8, 43.3)  # Kosovo
    assert "KOS" in skipped


def test_parse_bbox_valid_input():
    assert parse_bbox("88,22,90,26") == (88.0, 22.0, 90.0, 26.0)


def test_parse_bbox_handles_whitespace():
    assert parse_bbox("88, 22, 90, 26") == (88.0, 22.0, 90.0, 26.0)


def test_parse_bbox_wrong_count_raises():
    with pytest.raises(ValueError):
        parse_bbox("88,22,90")


def test_parse_bbox_non_numeric_raises():
    with pytest.raises(ValueError):
        parse_bbox("abc,22,90,26")


def test_parse_bbox_min_lon_not_less_than_max_lon_raises():
    with pytest.raises(ValueError):
        parse_bbox("90,22,88,26")


def test_parse_bbox_min_lat_not_less_than_max_lat_raises():
    with pytest.raises(ValueError):
        parse_bbox("88,26,90,22")


def test_parse_bbox_longitude_out_of_range_raises():
    with pytest.raises(ValueError):
        parse_bbox("-200,22,90,26")


def test_parse_bbox_latitude_out_of_range_raises():
    with pytest.raises(ValueError):
        parse_bbox("88,-100,90,26")
