"""Tests for weatherlab.plotting._format_visibility."""

import pandas as pd

from weatherlab.plotting import _format_visibility


def test_below_5km_shows_one_decimal():
    """WMO table 4377 is precise to 100 m below 5 km, so a decimal
    place reflects real precision rather than fabricating it."""
    assert _format_visibility(4000) == "4.0"


def test_below_5km_shows_real_fractional_precision():
    assert _format_visibility(3200) == "3.2"


def test_just_below_5km_boundary_shows_decimal():
    assert _format_visibility(4900) == "4.9"


def test_exactly_5km_shows_no_decimal():
    """At 5 km exactly, the code only resolves to 1 km steps, so a
    decimal would be false precision."""
    assert _format_visibility(5000) == "5"


def test_above_5km_shows_no_decimal():
    assert _format_visibility(10000) == "10"


def test_missing_value_returns_empty_string():
    assert _format_visibility(None) == ""
    assert _format_visibility(float("nan")) == ""
    assert _format_visibility(pd.NA) == ""
