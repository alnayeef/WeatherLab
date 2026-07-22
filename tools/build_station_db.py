import requests
import pandas as pd

API = "https://oscar.wmo.int/surface/rest/api/search/station"


def get_country(country_code):
    r = requests.get(
        API,
        params={
            "territoryName": country_code,
            "items": 50000,
            "page": 1,
        },
        headers={"User-Agent": "WeatherLab"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["stationSearchResults"]


stations = get_country("BGD")

rows = []

for s in stations:

    wigos = s.get("wigosId")

    if not wigos:
        continue

    wmo = wigos.split("-")[-1]

    rows.append({
        "wmo": wmo,
        "wigos": wigos,
        "name": s.get("name"),
        "country": s.get("territory"),
        "lat": s.get("latitude"),
        "lon": s.get("longitude"),
        "elev": s.get("hp"),
        "status": s.get("declaredStatus"),
        "type": s.get("stationTypeName"),
    })

df = pd.DataFrame(rows)

print(df.head())
print()
print("Stations:", len(df))

df.to_parquet("data/stations.parquet", index=False)

print("Saved data/stations.parquet")