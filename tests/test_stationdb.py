"""Tests for weatherlab.stationdb._wmo_from_wigos, confirming the
WIGOS issuer-range logic found during the original WMO OSCAR/Surface
research: only issuer values 20000-21999 mean the WIGOS ID's last
segment is a genuine legacy WMO number."""

from weatherlab.stationdb import _wmo_from_wigos


def test_legacy_wigos_id_returns_wmo_number():
    """Real Bangladesh example confirmed against the live OSCAR API."""
    assert _wmo_from_wigos("0-20000-0-41881") == "41881"


def test_post_2016_wigos_id_returns_none():
    """Real US example confirmed against the live OSCAR API - issuer
    840 is the US's own ISO 3166-1 numeric code, not a legacy-WMO
    issuer, so the last segment ('AFO') is a local identifier with no
    relationship to Ogimet's WMOIND field."""
    assert _wmo_from_wigos("0-840-0-AFO") is None


def test_issuer_boundary_20000_is_legacy():
    assert _wmo_from_wigos("0-20000-0-12345") == "12345"


def test_issuer_boundary_21999_is_legacy():
    assert _wmo_from_wigos("0-21999-0-12345") == "12345"


def test_issuer_just_below_legacy_range_returns_none():
    assert _wmo_from_wigos("0-19999-0-12345") is None


def test_issuer_just_above_legacy_range_returns_none():
    assert _wmo_from_wigos("0-22000-0-12345") is None


def test_missing_wigos_id_returns_none():
    assert _wmo_from_wigos(None) is None
    assert _wmo_from_wigos("") is None


def test_malformed_wigos_id_returns_none():
    assert _wmo_from_wigos("not-a-real-id") is None
    assert _wmo_from_wigos("0-20000-0") is None  # too few parts
