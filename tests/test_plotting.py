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


def test_create_map_with_explicit_extent_shows_exactly_that_box():
    """A lat/lon-box query needs the map to show exactly what was
    asked for, not a crop derived from wherever stations happened to
    be found (matches GrADS's own philosophy: showing the domain you
    asked for, not the domain your data happens to fill)."""
    import cartopy.crs as ccrs
    from weatherlab.plotting import create_map

    fig, ax = create_map(extent=(88, 90, 22, 26))
    lon_min, lon_max, lat_min, lat_max = ax.get_extent(crs=ccrs.PlateCarree())
    assert abs(lon_min - 88) < 0.01
    assert abs(lon_max - 90) < 0.01
    assert abs(lat_min - 22) < 0.01
    assert abs(lat_max - 26) < 0.01


def test_create_map_extent_takes_priority_over_obs():
    """If both are given, the explicit extent wins - obs-derived
    padding shouldn't silently override an exact user-requested box."""
    import pandas as pd
    import cartopy.crs as ccrs
    from weatherlab.plotting import create_map

    obs = pd.DataFrame([{"lon": 50.0, "lat": 10.0}])  # nowhere near the explicit extent
    fig, ax = create_map(obs=obs, extent=(88, 90, 22, 26))
    lon_min, lon_max, lat_min, lat_max = ax.get_extent(crs=ccrs.PlateCarree())
    assert abs(lon_min - 88) < 0.01
    assert abs(lon_max - 90) < 0.01


def test_create_map_with_explicit_extent_shows_exactly_that_box():
    """A lat/lon-box query needs the map to show exactly what was
    asked for, not a crop derived from wherever stations happened to
    be found (matches GrADS's own philosophy: showing the domain you
    asked for, not the domain your data happens to fill)."""
    import cartopy.crs as ccrs
    from weatherlab.plotting import create_map

    fig, ax = create_map(extent=(88, 90, 22, 26))
    lon_min, lon_max, lat_min, lat_max = ax.get_extent(crs=ccrs.PlateCarree())
    assert abs(lon_min - 88) < 0.01
    assert abs(lon_max - 90) < 0.01
    assert abs(lat_min - 22) < 0.01
    assert abs(lat_max - 26) < 0.01


def test_create_map_extent_takes_priority_over_obs():
    """If both are given, the explicit extent wins - obs-derived
    padding shouldn't silently override an exact user-requested box."""
    import pandas as pd
    import cartopy.crs as ccrs
    from weatherlab.plotting import create_map

    obs = pd.DataFrame([{"lon": 50.0, "lat": 10.0}])  # nowhere near the explicit extent
    fig, ax = create_map(obs=obs, extent=(88, 90, 22, 26))
    lon_min, lon_max, lat_min, lat_max = ax.get_extent(crs=ccrs.PlateCarree())
    assert abs(lon_min - 88) < 0.01
    assert abs(lon_max - 90) < 0.01
