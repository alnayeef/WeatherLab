import pandas as pd
import numpy as np
from metpy.calc import wind_components
from metpy.units import units
from .synop import get_raw_synop
from .decoder import decode_synop

def latest_surface_obs(country="Bang", hours_ago=0):
    """
    Download latest SYNOP observations for a given region and decode them.
    """
    # 1. Download raw data text matrix
    raw = get_raw_synop(country=country, hours_ago=hours_ago)

    if raw.empty:
        return pd.DataFrame()

    # 2. Decode each raw synop string row
        # 2. Decode each raw synop string row
    rows = []
    
    # --- FIX STEP: Dynamically find the text column ---
    # Look for common column names like 'synop_text', 'synop', or 'report'
    possible_cols = ["synop_text", "synop", "report", "text"]
    text_col = next((c for c in possible_cols if c in raw.columns), None)
    
    # Fallback: if none match, use the last column (usually where the text blob sits)
    if text_col is None:
        text_col = raw.columns[-1]

        print(f"[+] Extracting raw feeds from column: '{text_col}'")

    # --- FIX STEP: Map the exact column name discovered by diagnostics ---
    wmo_col = "WMOIND"

    for _, row in raw.iterrows():
        try:
            raw_text = row[text_col]
            if pd.isna(raw_text) or not str(raw_text).strip():
                continue
                
            decoded = decode_synop(raw_text)
            if decoded:
                decoded["wmo"] = row[wmo_col]
                rows.append(decoded)
        except Exception as e:
            continue

    obs = pd.DataFrame(rows)



    if obs.empty:
        print("Warning: All retrieved station reports for this hour were NIL or unparseable.")
        return pd.DataFrame()

        # 3. Handle wind fields cleanly
    obs["wind_speed"] = pd.to_numeric(obs["wind_speed"], errors="coerce").fillna(0.0)
    obs["wind_dir"] = pd.to_numeric(obs["wind_dir"], errors="coerce").fillna(0.0)

    # Force wind arrays to explicit floats to clear the Pint/radian mismatch completely
    speeds = obs["wind_speed"].values * units("knots")
    directions = obs["wind_dir"].values * units("degrees")

    u, v = wind_components(speeds, directions)
    obs["u"] = u.magnitude
    obs["v"] = v.magnitude

    print("[+] Appending universal coordinates via MetPy IO engine...")
    from metpy.io import add_station_lat_lon
    
    # CRITICAL CHANGE: Standardize WMO identifiers as clean, unpadded integers 
    # and name the column EXACTLY "wmo" so MetPy matches its master dictionary keys.
    obs["wmo"] = pd.to_numeric(obs["station"] if "station" in obs.columns else obs["wmo"], errors="coerce").astype(int)

    # Force MetPy to cross-reference our table based on the explicit 'wmo' ID index
    obs = add_station_lat_lon(obs, stn_var="wmo")

    # Adapt output names for the rendering scripts
    obs = obs.rename(columns={
        "latitude": "lat",
        "longitude": "lon"
    })

    # Drop any records that failed to map
    obs = obs.dropna(subset=["lon", "lat"])

    return obs



