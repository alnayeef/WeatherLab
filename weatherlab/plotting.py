import numpy as np

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from metpy.plots import StationPlot


def create_map():

    fig = plt.figure(figsize=(12, 9))

    ax = plt.axes(
        projection=ccrs.PlateCarree()
    )

    ax.set_extent(
        [88, 93.5, 20, 27],
        crs=ccrs.PlateCarree()
    )

    ax.add_feature(
        cfeature.COASTLINE,
        linewidth=0.8
    )

    ax.add_feature(
        cfeature.BORDERS,
        linewidth=0.6
    )

    ax.add_feature(
        cfeature.STATES,
        linewidth=0.4
    )

    return fig, ax


def plot_isobars(
    ax,
    LON,
    LAT,
    SLP
):

    levels = np.arange(
        np.floor(np.nanmin(SLP)),
        np.ceil(np.nanmax(SLP)),
        2
    )

    # If the pressure field is too flat, ensure we have at least one level to prevent errors
    if len(levels) == 0:
        levels = [1010]

    cs = ax.contour(
        LON,
        LAT,
        SLP,
        levels=levels,
        colors="black",
        linewidths=1.2,
        transform=ccrs.PlateCarree(),
        antialiased=True
    )

    ax.clabel(
        cs,
        inline=True,
        fmt="%d", # Force integers for clean chart labels
        fontsize=8
    )


def plot_station_model(
    ax,
    obs
):
    # --- TINY STEP: Drop rows missing latitude or longitude to avoid MetPy map errors ---
    valid_obs = obs.dropna(subset=["lon", "lat"]).copy()
    if valid_obs.empty:
        return

    # --- TINY STEP: Safely format numeric strings, leaving empty blanks for NaNs ---
    import pandas as pd
    
    temps = valid_obs["temp"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    dews = valid_obs["dewpoint"].apply(lambda x: f"{round(x)}" if pd.notna(x) else "")
    
    # Standard 3-digit SLP encoding (e.g., 1013.2 -> 132)
    slp = valid_obs["slp"].apply(
        lambda x: str(int(round(x * 10)) % 1000).zfill(3) if pd.notna(x) else ""
    )

    sp = StationPlot(
        ax,
        valid_obs["lon"].values,
        valid_obs["lat"].values,
        transform=ccrs.PlateCarree(),
        fontsize=8
    )

    sp.plot_text(
        "NW",
        temps.values
    )

    sp.plot_text(
        "SW",
        dews.values
    )

    sp.plot_text(
        "NE",
        slp.values
    )

    # --- TINY STEP: Fill missing wind vectors with 0 to prevent plotting errors ---
    u = valid_obs["u"].fillna(0).values
    v = valid_obs["v"].fillna(0).values
    
    sp.plot_barb(
        u,
        v
    )
