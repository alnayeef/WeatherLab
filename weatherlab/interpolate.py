"""Interpolate station pressure observations onto a regular grid for
isobar contouring."""

import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter


def pressure_field(obs, resolution=500, method="linear", smoothing=6):
    """
    Grid station SLP for contouring. Uses linear interpolation by
    default, not cubic - confirmed on real Bangladesh data that cubic
    can overshoot well past the actual station range in gaps between
    sparse stations (one real case: stations spanned 1001.4-1006.0
    hPa, cubic's grid reached 1014.77). Linear can't overshoot past
    its neighboring values by construction, and matched the real
    station range almost exactly in that same test - but being
    triangulation-based, contours through it come out as straight
    facet edges rather than smooth curves.

    smoothing (a Gaussian sigma, in grid cells) softens that into
    smooth curves afterward. Applied as a weighted smooth (smoothing
    the data and a validity mask together, then dividing back out)
    rather than a plain blur, so NaN gaps outside real station
    coverage can't bleed into nearby real cells - confirmed on real
    data that the NaN count is identical before and after, regardless
    of how large this value is. Pass 0 to disable and see the raw
    faceted linear grid.

    Cells outside the convex hull of the station points are left as
    NaN rather than filled - consistent with plotting.py, which
    already leaves those areas blank rather than drawing invented
    isobars where there's no real data.
    """
    valid_obs = obs.dropna(subset=["lon", "lat", "slp"])
    if len(valid_obs) < 3:
        raise ValueError("Not enough valid station reports to build a grid map.")
    x = valid_obs["lon"].values
    y = valid_obs["lat"].values
    z = valid_obs["slp"].values
    lon_min, lon_max = x.min() - 0.5, x.max() + 0.5
    lat_min, lat_max = y.min() - 0.5, y.max() + 0.5
    grid_lon = np.linspace(lon_min, lon_max, resolution)
    grid_lat = np.linspace(lat_min, lat_max, resolution)
    LON, LAT = np.meshgrid(grid_lon, grid_lat)
    SLP = griddata((x, y), z, (LON, LAT), method=method)

    if smoothing:
        nan_mask = np.isnan(SLP)
        filled = np.where(nan_mask, 0.0, SLP)
        weight = np.where(nan_mask, 0.0, 1.0)
        smoothed_values = gaussian_filter(filled, sigma=smoothing)
        smoothed_weight = gaussian_filter(weight, sigma=smoothing)
        with np.errstate(invalid="ignore", divide="ignore"):
            SLP = smoothed_values / smoothed_weight
        SLP[nan_mask] = np.nan

    return LON, LAT, SLP
