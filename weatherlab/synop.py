"""Fetch raw SYNOP reports from Ogimet for one country and one target hour."""

from datetime import timedelta
from io import StringIO

import pandas as pd
import requests

from .countries import resolve_country

OGIMET_API = "https://www.ogimet.com/cgi-bin/getsynop"
BRACKET = timedelta(minutes=10)
COLUMNS = ["WMOIND", "YEAR", "MONTH", "DAY", "HOUR", "MIN", "REPORT"]


def _deduplicate_by_distance(df, target_time):
    """
    When a station appears more than once (confirmed live: WMO's
    telecom network can relay the identical bulletin twice), keep
    whichever report is closest to target_time; if two are equally
    close, keep whichever appeared later in the original data
    (assumed to be a correction of the earlier one).
    """
    df = df.copy()
    df["_report_time"] = pd.to_datetime(
        dict(year=df.YEAR, month=df.MONTH, day=df.DAY, hour=df.HOUR, minute=df.MIN),
        utc=True,
    )
    df["_distance"] = (df["_report_time"] - target_time).abs()
    df["_orig_order"] = range(len(df))

    df = df.sort_values(["WMOIND", "_distance", "_orig_order"], ascending=[True, True, False])
    df = df.drop_duplicates("WMOIND", keep="first")
    return df.drop(columns=["_report_time", "_distance", "_orig_order"]).reset_index(drop=True)


def get_raw_synop(country_name, target_time):
    """
    Fetch raw SYNOP reports for one country, for the single synoptic hour
    closest to target_time (a timezone-aware UTC datetime). Returns an
    empty DataFrame if nothing is available for that hour - it does not
    fall back to a different hour.
    """
    country = resolve_country(country_name)
    r = requests.get(
        OGIMET_API,
        params={
            "begin": (target_time - BRACKET).strftime("%Y%m%d%H%M"),
            "end": (target_time + BRACKET).strftime("%Y%m%d%H%M"),
            "state": country.ogimet_name,
            "lang": "eng",
        },
        timeout=30,
    )
    r.raise_for_status()

    lines = [l.strip() for l in r.text.splitlines() if l.strip() and l.count(",") == 6]
    if not lines:
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_csv(StringIO("\n".join(lines)), names=COLUMNS, engine="python")
    return _deduplicate_by_distance(df, target_time)
