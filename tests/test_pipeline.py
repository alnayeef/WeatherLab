"""Tests for weatherlab.pipeline._add_wind_components, using the
exact known-correct values confirmed by hand against manual
trigonometry weeks ago, before this became a permanent test."""

import pandas as pd

from weatherlab.pipeline import _add_wind_components


def _single_row_result(wind_speed, wind_dir, wind_speed_unit):
    df = pd.DataFrame([{
        "wmo": "TEST",
        "wind_speed": wind_speed,
        "wind_dir": wind_dir,
        "wind_speed_unit": wind_speed_unit,
    }])
    return _add_wind_components(df).iloc[0]


def test_wind_components_knots():
    row = _single_row_result(2, 130, "knots")
    assert abs(row["u"] - (-0.79)) < 0.01
    assert abs(row["v"] - 0.66) < 0.01


def test_wind_components_meters_per_second():
    row = _single_row_result(41, 20, "m/s")
    assert abs(row["u"] - (-14.02)) < 0.01
    assert abs(row["v"] - (-38.53)) < 0.01


def test_wind_components_calm_gives_zero_regardless_of_direction():
    row = _single_row_result(0, None, "knots")
    assert row["u"] == 0.0
    assert row["v"] == 0.0


def test_wind_components_fully_missing_gives_nan():
    row = _single_row_result(None, None, None)
    assert pd.isna(row["u"])
    assert pd.isna(row["v"])


def test_wind_components_known_speed_missing_direction_gives_nan():
    """A real speed with a known unit but no direction must not
    silently compute a bogus vector - confirmed weeks ago that
    pymetdecoder can genuinely return this combination (a variable or
    undetermined direction alongside a known speed)."""
    row = _single_row_result(15, None, "knots")
    assert pd.isna(row["u"])
    assert pd.isna(row["v"])
