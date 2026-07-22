import numpy as np
from scipy.interpolate import griddata


def pressure_field(
    obs,
    resolution=500,
    method="cubic"
):

    # --- TINY STEP: Drop rows that are missing coordinates or pressure data ---
    valid_obs = obs.dropna(subset=["lon", "lat", "slp"])

    # If we don't have at least 3 stations, we can't interpolate a 2D surface map
    if len(valid_obs) < 3:
        raise ValueError("Not enough valid station reports to build a grid map.")

    # Use the cleaned data instead of the raw, messy 'obs' dataframe
    x = valid_obs["lon"].values
    y = valid_obs["lat"].values
    z = valid_obs["slp"].values

    lon_min = x.min() - 0.5
    lon_max = x.max() + 0.5

    lat_min = y.min() - 0.5
    lat_max = y.max() + 0.5

    grid_lon = np.linspace(
        lon_min,
        lon_max,
        resolution
    )

    grid_lat = np.linspace(
        lat_min,
        lat_max,
        resolution
    )

    LON, LAT = np.meshgrid(
        grid_lon,
        grid_lat
    )

    SLP = griddata(
        (x, y),
        z,
        (LON, LAT),
        method=method
    )

    mask = np.isnan(SLP)

    if np.any(mask):
        SLP[mask] = griddata(
            (x, y),
            z,
            (LON[mask], LAT[mask]),
            method="linear"
        )

    return LON, LAT, SLP
