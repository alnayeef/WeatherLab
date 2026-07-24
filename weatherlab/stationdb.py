"""Station metadata: fetch from WMO OSCAR/Surface, cached locally per country."""

from datetime import datetime, timedelta, UTC
from pathlib import Path

import pandas as pd
import platformdirs
import pycountry
import requests

OSCAR_API = "https://oscar.wmo.int/surface/rest/api/search/station"
CACHE_MAX_AGE = timedelta(days=30)


def _resolve_iso3(country_name):
    """Turn whatever a user types into the ISO3 code OSCAR expects."""
    match = pycountry.countries.search_fuzzy(country_name)
    return match[0].alpha_3


def _wmo_from_wigos(wigos_id):
    """Return the legacy 5-digit WMO number from a WIGOS ID, or None if
    this station was registered after 2016 and has no legacy number."""
    if not wigos_id:
        return None
    parts = wigos_id.split("-")
    if len(parts) != 4 or not parts[1].isdigit():
        return None
    issuer = int(parts[1])
    if 20000 <= issuer <= 21999:
        return parts[-1]
    return None


def _cache_path(iso3):
    cache_dir = Path(platformdirs.user_cache_dir("weatherlab"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"stations_{iso3}.parquet"


def _fetch_from_oscar(iso3):
    r = requests.get(
        OSCAR_API,
        params={"territoryName": iso3, "items": 50000, "page": 1},
        headers={"User-Agent": "WeatherLab"},
        timeout=60,
    )
    r.raise_for_status()
    raw = r.json()["stationSearchResults"]

    rows = []
    for s in raw:
        wmo = _wmo_from_wigos(s.get("wigosId"))
        if wmo is None:
            continue
        rows.append({
            "wmo": wmo,
            "name": s.get("name"),
            "lat": s.get("latitude"),
            "lon": s.get("longitude"),
            "declared_status": s.get("declaredStatus"),
            "assessed_status": s.get("assessedStatus"),
        })
    df = pd.DataFrame(rows)

    dup_count = int(df["wmo"].duplicated().sum())
    if dup_count:
        print(f"[stationdb] {dup_count} duplicate WMO IDs for {iso3}; keeping the Operational entry where one exists.")
        df["_priority"] = (df["declared_status"] != "Operational").astype(int)
        df = df.sort_values("_priority").drop_duplicates("wmo", keep="first").drop(columns="_priority")

    return df


class StationDB:
    """Station metadata for one country, fetched from WMO OSCAR/Surface
    and cached locally so repeat runs don't hit the network."""

    def __init__(self, country_name, max_age=CACHE_MAX_AGE):
        self.iso3 = _resolve_iso3(country_name)
        path = _cache_path(self.iso3)

        age = None
        if path.exists():
            age = datetime.now(UTC) - datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)

        if age is None or age > max_age:
            print(f"[stationdb] Fetching {country_name} stations from OSCAR...")
            df = _fetch_from_oscar(self.iso3)
            df.to_parquet(path, index=False)
        else:
            print(f"[stationdb] Using cached {country_name} stations ({age.days} day(s) old).")
            df = pd.read_parquet(path)

        self.df = df.set_index("wmo")

    def lookup_wmo(self, wmo):
        try:
            return self.df.loc[str(wmo)].to_dict()
        except KeyError:
            return None
