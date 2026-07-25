"""Decode raw SYNOP reports using pymetdecoder, with a best-effort
manual fallback for reports pymetdecoder can't parse."""

from pymetdecoder import synop

# pymetdecoder reports wind units using WMO-style abbreviations that
# Pint's registry doesn't recognize directly - confirmed on live data,
# where 'KT' raised UndefinedUnitError. Normalized here so any caller
# can always do units(wind_speed_unit) without knowing this quirk.
_WIND_UNIT_MAP = {"KT": "knots"}

# WMO code table 1855 (the iw digit in the YYGGiw group): what unit
# the wind speed group is actually reported in. 0/1 is m/s, 3/4 is
# knots, '/' (confirmed live, on a US report) means the station
# didn't specify - confirmed against the official WMO manual.
_WIND_UNIT_BY_IW = {"0": "m/s", "1": "m/s", "3": "knots", "4": "knots"}


def _normalize_wind_unit(unit):
    if unit is None:
        return None
    return _WIND_UNIT_MAP.get(unit, unit)


def _finalize(result):
    """Enforce one invariant regardless of which path produced this
    dict: a wind speed with no known unit isn't safely usable, so
    it's dropped rather than passed along unlabeled. pymetdecoder's
    own primary decode can leave a speed value with no unit attached
    - this is the actual gap the previous, fallback-only fix missed."""
    if result is None:
        return None
    if result.get("wind_speed") is not None and result.get("wind_speed_unit") is None:
        result["wind_dir"] = None
        result["wind_speed"] = None
    return result


def decode_synop(report):
    report_clean = str(report).strip()
    if "AAXX" in report_clean:
        report_clean = report_clean[report_clean.index("AAXX"):]

    try:
        data = synop.SYNOP().decode(report_clean)
        wind_speed = data.get("surface_wind", {}).get("speed", {})
        return _finalize({
            "temp": data.get("air_temperature", {}).get("value"),
            "dewpoint": data.get("dewpoint_temperature", {}).get("value"),
            "slp": data.get("sea_level_pressure", {}).get("value"),
            "wind_dir": data.get("surface_wind", {}).get("direction", {}).get("value"),
            "wind_speed": wind_speed.get("value"),
            "wind_speed_unit": _normalize_wind_unit(wind_speed.get("unit")),
            "cloud_cover": data.get("cloud_cover", {}).get("value"),
            "visibility": data.get("visibility", {}).get("value"),
            "present_weather": data.get("present_weather", {}).get("value"),
        })
    except Exception:
        return _finalize(manual_fallback_parse(report_clean))


def manual_fallback_parse(text):
    """
    Best-effort parse for reports pymetdecoder can't handle. Recovers
    temp, dewpoint, SLP, and wind - the unit-consistency rule for wind
    is enforced centrally by _finalize, not here, so both decode
    paths share exactly one copy of that logic. cloud_cover,
    visibility, and present_weather always come back None here, since
    reliably hand-parsing their group positions is much closer to
    reimplementing pymetdecoder than a fallback should attempt.
    """
    tokens = text.replace('=', '').split()
    if len(tokens) < 3:
        return None

    iw = tokens[1][-1]
    wind_unit = _WIND_UNIT_BY_IW.get(iw)

    # Skip AAXX, YYGGiw, IIiii - never data groups, and the station ID
    # itself can start with any digit (Bangladesh's own IDs start with
    # '4', which previously got misread as a pressure group).
    body = tokens[3:]

    temp, dewpoint, slp = None, None, None
    for t in body:
        clean = t.replace('/', '')
        if not clean.isdigit() or len(clean) != 5:
            continue
        if clean.startswith('1'):
            sign = -1 if clean[1] == '1' else 1
            temp = sign * (int(clean[2:]) / 10.0)
        elif clean.startswith('2'):
            sign = -1 if clean[1] == '1' else 1
            dewpoint = sign * (int(clean[2:]) / 10.0)
        elif clean.startswith('4'):
            val = int(clean[1:]) / 10.0
            slp = val + 1000.0 if val < 500.0 else val

    wind_dir, wind_speed = None, None
    for t in body[:2]:
        if len(t) == 5 and t.isdigit():
            try:
                wind_dir = int(t[1:3]) * 10
                wind_speed = int(t[3:])
            except ValueError:
                pass
    if wind_speed == 0:
        wind_dir = None

    if temp is None and slp is None:
        return None
    return {
        "temp": temp, "dewpoint": dewpoint, "slp": slp,
        "wind_dir": wind_dir, "wind_speed": wind_speed,
        "wind_speed_unit": wind_unit,
        "cloud_cover": None, "visibility": None, "present_weather": None,
    }
