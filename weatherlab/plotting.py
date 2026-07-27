"""Draw surface weather charts: base map, isobars, and station models."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.calc import reduce_point_density
from metpy.plots import StationPlot, sky_cover, current_weather


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


def plot_isobars(ax, LON, LAT, SLP, interval=4):
    """Isobars at fixed, conventional 4 hPa intervals by default -
    snapped to fixed multiples of `interval`, not derived from
    today's min/max. A real hand-analysis chart draws the same
    physical pressure at the same line every time; deriving the
    interval from whatever data happens to come in would draw a
    different set of lines every run, even for near-identical
    weather."""
    low = np.floor(np.nanmin(SLP) / interval) * interval
    high = np.ceil(np.nanmax(SLP) / interval) * interval
    levels = np.arange(low, high + interval, interval)
    if len(levels) == 0:
        levels = [1012]  # nearest standard multiple of 4 to average sea-level pressure
    cs = ax.contour(
        LON, LAT, SLP, levels=levels, colors="black", linewidths=1.2,
        transform=ccrs.PlateCarree(), antialiased=True,
    )
    ax.clabel(cs, inline=True, fmt="%d", fontsize=8)


def _format_visibility(x):
    """Below 5 km, WMO table 4377 is precise to 100 m, so one decimal
    place reflects real precision. At or above 5 km, the code only
    resolves to 1 km steps, so a decimal would be false precision -
    shown as a clean integer instead."""
    if pd.isna(x):
        return ""
    km = x / 1000
    return f"{km:.1f}" if x < 5000 else f"{km:.0f}"


def plot_station_model(ax, obs, fontsize=4, symbol_fontsize=9, barb_length=5.75,
                        spacing=8.5, min_radius=0.3):
    """Plot the full station model. Text and present-weather symbols
    use fontsize (kept small - numbers and glyphs meant to be read up
    close); cloud cover and the wind barb get their own larger sizes,
    since they're meant to read as shapes from a distance. spacing
    widens the gaps between every element so nearby stations overlap
    less. Missing wind is left undrawn rather than shown as a fake
    calm; missing cloud cover, present weather, or visibility are
    each simply left blank at that station.

    Visibility sits at (-2, 0) - two spacing units directly left of
    center, one step further out than present weather at "W" (-1, 0)
    - matching the traditional station model, where the two share the
    horizontal midline between temperature (NW) and dewpoint (SW),
    visibility being the outer of the two.

    min_radius controls station thinning (MetPy's reduce_point_density,
    in degrees): stations closer than this to an already-kept one are
    skipped so dense clusters stay legible. Pass None to draw every
    decoded station regardless of crowding - the caller's choice, not
    forced here. Either way, only affects what gets drawn here;
    pressure_field() still interpolates from every report.
    """
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
