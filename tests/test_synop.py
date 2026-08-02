"""Tests for weatherlab.synop._deduplicate_by_distance."""

from datetime import datetime, UTC

import pandas as pd

from weatherlab.synop import _deduplicate_by_distance

TARGET = datetime(2026, 7, 23, 21, 0, tzinfo=UTC)


def _row(wmoind, hour, minute, report):
    return {
        "WMOIND": wmoind, "YEAR": 2026, "MONTH": 7, "DAY": 23,
        "HOUR": hour, "MIN": minute, "REPORT": report,
    }


def test_no_duplicates_passes_through_unchanged():
    df = pd.DataFrame([_row(33333, 21, 0, "UNIQUE_REPORT")])
    result = _deduplicate_by_distance(df, TARGET)
    assert len(result) == 1
    assert result.iloc[0]["REPORT"] == "UNIQUE_REPORT"


def test_duplicate_keeps_report_closest_to_target():
    """The one real live duplicate found during development happened
    to be byte-identical, so this tiebreak was never actually
    exercised on genuinely differing content until now."""
    df = pd.DataFrame([
        _row(11111, 20, 58, "CLOSER_REPORT"),   # 2 minutes before target
        _row(11111, 21, 5, "FARTHER_REPORT"),   # 5 minutes after target
    ])
    result = _deduplicate_by_distance(df, TARGET)
    assert len(result) == 1
    assert result.iloc[0]["REPORT"] == "CLOSER_REPORT"


def test_duplicate_with_equal_distance_keeps_later_transmission():
    """When two reports are equally close to target_time, the one
    that appeared later in the original data is kept, on the
    assumption it's a correction of the earlier one."""
    df = pd.DataFrame([
        _row(22222, 20, 55, "EARLIER_TRANSMISSION"),  # 5 minutes before
        _row(22222, 21, 5, "LATER_TRANSMISSION"),      # 5 minutes after
    ])
    result = _deduplicate_by_distance(df, TARGET)
    assert len(result) == 1
    assert result.iloc[0]["REPORT"] == "LATER_TRANSMISSION"


def test_multiple_stations_deduplicated_independently():
    df = pd.DataFrame([
        _row(11111, 20, 58, "CLOSER_REPORT"),
        _row(11111, 21, 5, "FARTHER_REPORT"),
        _row(33333, 21, 0, "UNIQUE_REPORT"),
    ])
    result = _deduplicate_by_distance(df, TARGET)
    assert len(result) == 2
    kept = result[result["WMOIND"] == 11111].iloc[0]
    assert kept["REPORT"] == "CLOSER_REPORT"
