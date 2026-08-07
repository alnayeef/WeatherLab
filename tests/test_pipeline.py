"""Tests for weatherlab.pipeline._add_wind_components and
_filter_to_bbox, using the exact known-correct values confirmed by
hand against manual trigonometry weeks ago, before this became a
permanent test."""

import pandas as pd

from weatherlab.pipeline import _add_wind_components, _filter_to_bbox


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
    row = _single_row_result(15, None, "knots")
    assert pd.isna(row["u"])
    assert pd.isna(row["v"])


def test_filter_to_bbox_keeps_only_stations_inside():
    df = pd.DataFrame([
        {"wmo": "INSIDE", "lon": 90.0, "lat": 24.0},
        {"wmo": "OUTSIDE_LON", "lon": 100.0, "lat": 24.0},
        {"wmo": "OUTSIDE_LAT", "lon": 90.0, "lat": 40.0},
    ])
    result = _filter_to_bbox(df, min_lon=89, min_lat=23, max_lon=91, max_lat=25)
    assert list(result["wmo"]) == ["INSIDE"]


def test_filter_to_bbox_boundary_is_inclusive():
    """A station exactly on the box edge should be kept, not
    excluded by a strict inequality."""
    df = pd.DataFrame([{"wmo": "ON_EDGE", "lon": 89.0, "lat": 24.0}])
    result = _filter_to_bbox(df, min_lon=89, min_lat=23, max_lon=91, max_lat=25)
    assert len(result) == 1
