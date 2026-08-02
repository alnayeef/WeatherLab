"""Tests for weatherlab.interpolate.pressure_field, confirming the
two properties found through direct investigation weeks ago: linear
interpolation can't overshoot past the real station range (unlike
the cubic method originally used), and NaN-preserving smoothing
doesn't let gaps outside real coverage bleed into real cells."""

import numpy as np
import pandas as pd
import pytest

from weatherlab.interpolate import pressure_field

THREE_STATIONS = pd.DataFrame([
    {"lon": 90.0, "lat": 20.0, "slp": 1000.0},
    {"lon": 91.0, "lat": 20.0, "slp": 1010.0},
    {"lon": 90.5, "lat": 21.0, "slp": 1005.0},
])


def test_pressure_field_raises_with_too_few_stations():
    df = pd.DataFrame([{"lon": 90, "lat": 20, "slp": 1000}, {"lon": 91, "lat": 21, "slp": 1010}])
    with pytest.raises(ValueError):
        pressure_field(df)


def test_pressure_field_linear_does_not_overshoot():
    """Regression test: cubic interpolation, used originally, could
    exceed the real station range in gaps between sparse stations -
    confirmed live on real Bangladesh data (stations spanning
    1001.4-1006.0 hPa, cubic's grid reaching 1014.77). Linear can't,
    by construction - it's a convex combination of each triangle's
    own vertex values."""
    _, _, SLP = pressure_field(THREE_STATIONS, resolution=50, smoothing=0)
    assert np.nanmin(SLP) >= 1000.0 - 0.01
    assert np.nanmax(SLP) <= 1010.0 + 0.01


def test_pressure_field_smoothing_preserves_nan_mask():
    """Regression test: a plain Gaussian blur would let NaN gaps
    outside real station coverage bleed into nearby real cells -
    confirmed live that the weighted-smoothing approach keeps the
    exact same NaN count before and after, regardless of sigma."""
    _, _, unsmoothed = pressure_field(THREE_STATIONS, resolution=50, smoothing=0)
    _, _, smoothed = pressure_field(THREE_STATIONS, resolution=50, smoothing=3)
    assert np.isnan(unsmoothed).sum() == np.isnan(smoothed).sum()
