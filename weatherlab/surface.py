import matplotlib.pyplot as plt

from weatherlab.plotting import (
    create_map,
    plot_isobars,
    plot_station_model
)
# --- TINY STEP: Import your interpolation logic ---
from weatherlab.interpolate import pressure_field


def surface_analysis(obs):

    fig, ax = create_map()

    # --- TINY STEP: Generate the 2D grid before drawing lines ---
    try:
        LON, LAT, SLP = pressure_field(obs)
        plot_isobars(ax, LON, LAT, SLP)
    except Exception as e:
        print(f"Could not plot isobars: {e}")

    # Plot individual station models on top
    plot_station_model(ax, obs)

    return fig, ax
