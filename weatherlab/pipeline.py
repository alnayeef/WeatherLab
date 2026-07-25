"""Orchestrate fetching, decoding, and geolocating SYNOP observations
for one country and one target synoptic hour."""

import pandas as pd
from metpy.units import units
from metpy.calc import wind_components

from .synop import get_raw_synop
from .decoder import decode_synop
from .stationdb import StationDB


def surface_obs(country_name, target_time):
    """
    Returns a DataFrame ready for interpolation and plotting - one row
    per station, lat/lon and u/v wind already attached. Empty if
    nothing could be decoded and matched to a known station.
    """
    raw = get_raw_synop(country_name, target_time)
    if raw.empty:
        return pd.DataFrame()

    db = StationDB(country_name)

    rows = []
    for row in raw.itertuples():
        decoded = decode_synop(row.REPORT)
        if decoded is None:
            continue
        station = db.lookup_wmo(row.WMOIND)
        if station is None:
            continue
        decoded.update(station)
        decoded["wmo"] = str(row.WMOIND)
        rows.append(decoded)

    print(f"[pipeline] {len(rows)} of {len(raw)} station report(s) decoded and matched.")

    if not rows:
        return pd.DataFrame()

    return _add_wind_components(pd.DataFrame(rows))


def _add_wind_components(df):
    """Tested separately against known-correct values for both knots
    and m/s. Calm gives (0, 0); anything unknown gives (None, None)."""
    u_list, v_list = [], []
    for row in df.itertuples():
        speed, direction, unit = row.wind_speed, row.wind_dir, row.wind_speed_unit
        if speed == 0:
            u_list.append(0.0)
            v_list.append(0.0)
        elif pd.isna(speed) or pd.isna(direction) or pd.isna(unit):
            u_list.append(None)
            v_list.append(None)
        else:
            speed_q = speed * units(unit)
            direction_q = direction * units("degrees")
            u, v = wind_components(speed_q, direction_q)
            u_list.append(u.to("m/s").magnitude)
            v_list.append(v.to("m/s").magnitude)
    df = df.copy()
    df["u"] = u_list
    df["v"] = v_list
    return df
