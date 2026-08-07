"""Draw surface weather charts: base map, isobars, and station models."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.calc import reduce_point_density
from metpy.plots import StationPlot, sky_cover, current_weather


def create_map(obs=None, padding=0.5, ax=None, extent=None):
    """Create (or reconfigure) a map axes. Three ways to control what
    it shows, in priority order:
    - extent=(lon_min, lon_max, lat_min, lat_max): show exactly this
      area regardless of where any actual data sits - what a lat/lon
      box query needs, so the map reflects the exact area requested,
      not a crop of it based on wherever stations happened to be
      found.
    - obs given, no extent: derive it from the station spread, with
      padding - the country-selection case, where there's no
      user-specified exact box to show instead.
    - neither: blank view, nothing plotted yet.

    Pass ax to reuse an existing cartopy axes instead of creating a
    new figure - clears it first. This is what lets the interactive
    shell redraw onto the same window across repeated `plot` commands
    rather than opening a new one each time; the one-shot CLI path
    doesn't need this and can keep calling this with ax=None exactly
    as before.
    """
    if ax is None:
        fig = plt.figure(figsize=(12, 9))
        ax = plt.axes(projection=ccrs.PlateCarree())
    else:
        fig = ax.figure
        ax.clear()

    if extent is None and obs is not None and not obs.empty:
        extent = (
            obs["lon"].min() - padding, obs["lon"].max() + padding,
            obs["lat"].min() - padding, obs["lat"].max() + padding,
        )

    if extent is not None:
        ax.set_axis_on()
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.6)
        ax.add_feature(cfeature.STATES, linewidth=0.4)
    else:
        ax.set_axis_off()

    return fig, ax


def plot_isobars(ax, LON, LAT, SLP, interval=4):
    low = np.floor(np.nanmin(SLP) / interval) * interval
    high = np.ceil(np.nanmax(SLP) / interval) * interval
    levels = np.arange(low, high + interval, interval)
    if len(levels) == 0:
        levels = [1012]
    cs = ax.contour(
        LON, LAT, SLP, levels=levels, colors="black", linewidths=1.2,
        transform=ccrs.PlateCarree(), antialiased=True,
    )
    ax.clabel(cs, inline=True, fmt="%d", fontsize=8)


def _format_visibility(x):
    if pd.isna(x):
        return ""
    km = x / 1000
    return f"{km:.1f}" if x < 5000 else f"{km:.0f}"


def default_filename(country, time):
    """Standard filename for a saved chart: <country>_<time>.png, with
    spaces and colons replaced so it's safe as a filename on any OS."""
    return f"{country.replace(' ', '_')}_{time.replace(' ', '_').replace(':', '')}.png"


def plot_station_model(ax, obs, fontsize=4, symbol_fontsize=9, barb_length=5.75,
                        spacing=8.5, min_radius=0.3):
    valid_obs = obs.dropna(subset=["lon", "lat"]).copy()
    if valid_obs.empty:
        return

    if min_radius is not None:
        mask = reduce_point_density(valid_obs[["lon", "lat"]].values, min_radius)
        valid_obs = valid_obs[mask]

    temps = valid_obs["temp"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    dews = valid_obs["dewpoint"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    slp = valid_obs["slp"].apply(
        lambda x: str(int(round(x * 10)) % 1000).zfill(3) if pd.notna(x) else ""
    )
    vis = valid_obs["visibility"].apply(_format_visibility)
    cloud_vals = [int(x) if pd.notna(x) else float("nan") for x in valid_obs["cloud_cover"]]
    wx_vals = [int(x) if pd.notna(x) else float("nan") for x in valid_obs["present_weather"]]

    sp = StationPlot(
        ax, valid_obs["lon"].values, valid_obs["lat"].values,
        transform=ccrs.PlateCarree(), fontsize=fontsize, spacing=spacing,
    )
    sp.plot_text("NW", temps.values)
    sp.plot_text("SW", dews.values)
    sp.plot_text("NE", slp.values)
    sp.plot_text((-2, 0), vis.values)
    sp.plot_symbol("C", cloud_vals, sky_cover, fontsize=symbol_fontsize)
    sp.plot_symbol("W", wx_vals, current_weather)
    sp.plot_barb(valid_obs["u"].values, valid_obs["v"].values, length=barb_length)
