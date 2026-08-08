"""Resolve a lat/lon bounding box: parse it from user input, find
which countries it overlaps, and convert those to country names
usable by the rest of the pipeline."""

import cartopy.io.shapereader as shpreader
import pycountry
from shapely.geometry import box


def parse_bbox(text):
    """
    Parse a "min_lon,min_lat,max_lon,max_lat" string into a validated
    (min_lon, min_lat, max_lon, max_lat) tuple of floats. Raises
    ValueError with a specific, actionable message for anything
    malformed, so bad input is rejected immediately - not partway
    through a live fetch.

    Boxes crossing the antimeridian (e.g. spanning from 170 to -170
    longitude) aren't supported - min_lon must be less than max_lon,
    same as latitude.
    """
    parts = text.split(",")
    if len(parts) != 4:
        raise ValueError(
            f"Expected 4 comma-separated values (min_lon,min_lat,max_lon,max_lat), got {len(parts)}."
        )
    try:
        min_lon, min_lat, max_lon, max_lat = (float(p.strip()) for p in parts)
    except ValueError:
        raise ValueError(f"All 4 values must be numbers: {text!r}")

    if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
        raise ValueError("Longitude values must be between -180 and 180.")
    if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
        raise ValueError("Latitude values must be between -90 and 90.")
    if min_lon >= max_lon:
        raise ValueError(f"min_lon ({min_lon}) must be less than max_lon ({max_lon}).")
    if min_lat >= max_lat:
        raise ValueError(f"min_lat ({min_lat}) must be less than max_lat ({max_lat}).")

    return (min_lon, min_lat, max_lon, max_lat)


def _load_country_records():
    shapefile = shpreader.natural_earth(
        resolution="110m", category="cultural", name="admin_0_countries"
    )
    return list(shpreader.Reader(shapefile).records())


def countries_in_bbox(min_lon, min_lat, max_lon, max_lat):
    """
    Returns the ISO3 codes of every country whose actual shape
    intersects the given box - not just whose bounding box overlaps
    it. A handful of Natural Earth records (disputed or
    partially-recognized territories: Norway, France, N. Cyprus,
    Somaliland, Kosovo) have no standard ISO_A3 code at all; ADM0_A3
    (Natural Earth's own code, present for every record) is used only
    for those, since it disagrees with ISO_A3 for several ordinary,
    universally-recognized countries elsewhere in the dataset -
    confirmed directly, not assumed - and ISO_A3 is what needs to
    match resolve_country() and everything built on top of it.
    """
    user_box = box(min_lon, min_lat, max_lon, max_lat)
    codes = []
    for record in _load_country_records():
        if record.geometry.intersects(user_box):
            iso3 = record.attributes["ISO_A3"]
            if iso3 == "-99":
                iso3 = record.attributes["ADM0_A3"]
            codes.append(iso3)
    return codes


def resolve_bbox_countries(min_lon, min_lat, max_lon, max_lat):
    """
    Returns (names, skipped) for every country a bbox touches - names
    are country name strings usable exactly like a single --country
    value already is (with surface_obs, StationDB, get_raw_synop);
    skipped is the ISO3 codes that couldn't be resolved that way.

    A few of countries_in_bbox()'s codes are Natural Earth's own
    codes for disputed or partially-recognized territories with no
    pycountry entry at all - confirmed live: Northern Cyprus (CYN),
    Somaliland (SOL), Kosovo (KOS). There's no reliable way to fetch
    OSCAR/Ogimet data for these under this project's country-name
    architecture, so they're skipped rather than raising - reported
    back explicitly, not silently dropped, so a bbox covering one of
    these alongside a normal country still returns real data for the
    rest instead of failing entirely.
    """
    codes = countries_in_bbox(min_lon, min_lat, max_lon, max_lat)
    names, skipped = [], []
    for code in codes:
        country = pycountry.countries.get(alpha_3=code)
        if country is None:
            skipped.append(code)
        else:
            names.append(country.name)
    return names, skipped
