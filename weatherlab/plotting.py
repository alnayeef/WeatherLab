"""Draw surface weather charts: base map, isobars, and station models."""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.plots import StationPlot


def create_map(obs, padding=0.5):
    """Base map sized to fit the given stations, with padding around
    the outermost ones - same padding interpolate.py already uses for
    its grid, so the map extent and the isobar grid line up."""
    lon_min = obs["lon"].min() - padding
    lon_max = obs["lon"].max() + padding
    lat_min = obs["lat"].min() - padding
    lat_max = obs["lat"].max() + padding

    fig = plt.figure(figsize=(12, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.6)
    ax.add_feature(cfeature.STATES, linewidth=0.4)
    return fig, ax


def plot_isobars(ax, LON, LAT, SLP):
    levels = np.arange(np.floor(np.nanmin(SLP)), np.ceil(np.nanmax(SLP)), 2)
    if len(levels) == 0:
        levels = [1010]
    cs = ax.contour(
        LON, LAT, SLP, levels=levels, colors="black", linewidths=1.2,
        transform=ccrs.PlateCarree(), antialiased=True,
    )
    ax.clabel(cs, inline=True, fmt="%d", fontsize=8)


def plot_station_model(ax, obs):
    """Plot temp/dewpoint/SLP text and wind barbs for each station.
    Missing wind (NaN u/v) is left undrawn rather than shown as a
    fake calm - matches the calm-vs-missing distinction already made
    throughout the decode pipeline."""
    valid_obs = obs.dropna(subset=["lon", "lat"]).copy()
    if valid_obs.empty:
        return
    import pandas as pd

    temps = valid_obs["temp"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    dews = valid_obs["dewpoint"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    # Standard 3-digit SLP encoding (e.g., 1013.2 -> 132)
    slp = valid_obs["slp"].apply(
        lambda x: str(int(round(x * 10)) % 1000).zfill(3) if pd.notna(x) else ""
    )
    sp = StationPlot(
        ax, valid_obs["lon"].values, valid_obs["lat"].values,
        transform=ccrs.PlateCarree(), fontsize=8,
    )
    sp.plot_text("NW", temps.values)
    sp.plot_text("SW", dews.values)
    sp.plot_text("NE", slp.values)

    sp.plot_barb(valid_obs["u"].values, valid_obs["v"].values)
