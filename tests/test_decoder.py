"""Tests for weatherlab.decoder, using real SYNOP reports and known
bug cases found during development."""

import warnings

from weatherlab.decoder import manual_fallback_parse, decode_synop, _finalize

BANGLADESH_REPORT = "AAXX 23214 41850 31440 40000 10262 20250 39927 40026 70511 82510 333 56990 59015 70120 82618 84460="
US_REPORT = "AAXX 2503/ 72613 42989 02811 10089 20057 38162 51003="
GARBLED_WIND_REPORT = "AAXX 23214 41850 31440 4//// 10262 20250 39927 40026="


def test_manual_fallback_parse_bangladesh():
    result = manual_fallback_parse(BANGLADESH_REPORT)
    assert result["temp"] == 26.2
    assert result["dewpoint"] == 25.0
    assert result["slp"] == 1002.6
    assert result["wind_dir"] is None
    assert result["wind_speed"] == 0


def test_manual_fallback_parse_us_report_slp_not_fabricated():
    """Regression test: iRixhVV's leading '4' (in '42989') was
    previously misread as a fabricated 4PPPP pressure group when no
    real one was present, computing a physically impossible 1298.9
    hPa instead of correctly returning None."""
    result = manual_fallback_parse(US_REPORT)
    assert result["temp"] == 8.9
    assert result["dewpoint"] == 5.7
    assert result["slp"] is None


def test_manual_fallback_parse_garbled_wind():
    result = manual_fallback_parse(GARBLED_WIND_REPORT)
    assert result["wind_dir"] is None
    assert result["wind_speed"] is None
    assert result["wind_speed_unit"] is None


def test_decode_synop_us_report_full_values():
    """Confirms every field decode_synop actually extracts for this
    report, now that the '=' end-of-report marker is stripped before
    handing it to pymetdecoder."""
    result = decode_synop(US_REPORT)
    assert result["temp"] == 8.9
    assert result["dewpoint"] == 5.7
    assert result["slp"] is None
    assert result["wind_dir"] is None
    assert result["wind_speed"] is None
    assert result["cloud_cover"] == 0
    assert result["visibility"] == 70000


def test_decode_synop_us_report_no_spurious_warning():
    """Regression test: decode_synop previously handed pymetdecoder
    this report with '=' still glued onto the last group ('51003='),
    which was then rejected as not matching the expected 5-character
    group pattern - even though '51003' alone is a genuinely valid
    5appp pressure-tendency group (confirmed against the actual
    meteorological code table, not just by the absence of a crash)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        decode_synop(US_REPORT)
    assert len(caught) == 0, f"Unexpected warning(s): {[str(w.message) for w in caught]}"


def test_finalize_drops_speed_with_no_known_unit():
    result = _finalize({"wind_speed": 10, "wind_speed_unit": None, "wind_dir": 90, "temp": 20})
    assert result["wind_speed"] is None
    assert result["wind_dir"] is None


def test_finalize_keeps_speed_with_known_unit():
    result = _finalize({"wind_speed": 10, "wind_speed_unit": "knots", "wind_dir": 90, "temp": 20})
    assert result["wind_speed"] == 10
    assert result["wind_dir"] == 90


def test_finalize_handles_none():
    assert _finalize(None) is None
