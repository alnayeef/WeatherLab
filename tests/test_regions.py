"""Tests for weatherlab.regions.countries_in_bbox."""

from weatherlab.regions import countries_in_bbox


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
