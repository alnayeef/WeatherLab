"""Orchestrate fetching, decoding, and geolocating SYNOP observations
for one country (or a lat/lon box spanning several) and one target
synoptic hour."""

import pandas as pd
from metpy.units import units
from metpy.calc import wind_components

from .synop import get_raw_synop
from .decoder import decode_synop
from .stationdb import StationDB
from .regions import resolve_bbox_countries


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

    print(f"[pipeline] {country_name}: {len(rows)} of {len(raw)} station report(s) decoded and matched.")

    if not rows:
        return pd.DataFrame()

    return _add_wind_components(pd.DataFrame(rows))


def surface_obs_bbox(min_lon, min_lat, max_lon, max_lat, target_time):
    """
    Fetch and decode observations for every country the box touches,
    then filter down to just the stations whose actual coordinates
    land inside the box - a station just across a border shouldn't
    appear on the final chart just because its whole country got
    fetched.

    Returns (obs, skipped): obs is shaped exactly like surface_obs()'s
    return value; skipped is the ISO3 codes of any disputed
    territories the box touches that couldn't be resolved to a
    fetchable country name (see resolve_bbox_countries) - reported
    back explicitly rather than silently dropped or raised as an
    error.
    """
    country_names, skipped = resolve_bbox_countries(min_lon, min_lat, max_lon, max_lat)
    if not country_names:
        return pd.DataFrame(), skipped

    frames = [surface_obs(name, target_time) for name in country_names]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame(), skipped

    combined = pd.concat(frames, ignore_index=True)
    return _filter_to_bbox(combined, min_lon, min_lat, max_lon, max_lat), skipped


def _filter_to_bbox(df, min_lon, min_lat, max_lon, max_lat):
    """Keep only rows whose lon/lat actually falls inside the box -
    needed because a country-wide fetch includes every station in
    that country, not just the ones inside the requested box."""
    return df[
        (df["lon"] >= min_lon) & (df["lon"] <= max_lon) &
        (df["lat"] >= min_lat) & (df["lat"] <= max_lat)
    ].reset_index(drop=True)


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
