"""Resolve a lat/lon bounding box to the ISO3 country codes it
overlaps, using Natural Earth's country boundaries (already cached
locally by cartopy) and a real geometric intersection - a simple
min/max bounding-box comparison would incorrectly match countries
split across the antimeridian, like Fiji, whose naive bounds span
the entire globe's longitude range."""

import cartopy.io.shapereader as shpreader
import pycountry
from shapely.geometry import box


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
