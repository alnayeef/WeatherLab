"""Decode raw SYNOP reports using pymetdecoder, with a best-effort
manual fallback for reports pymetdecoder can't parse."""

from pymetdecoder import synop

_WIND_UNIT_MAP = {"KT": "knots"}
_WIND_UNIT_BY_IW = {"0": "m/s", "1": "m/s", "3": "knots", "4": "knots"}


def _normalize_wind_unit(unit):
    if unit is None:
        return None
    return _WIND_UNIT_MAP.get(unit, unit)


def _finalize(result):
    if result is None:
        return None
    if result.get("wind_speed") is not None and result.get("wind_speed_unit") is None:
        result["wind_dir"] = None
        result["wind_speed"] = None
    return result


def decode_synop(report):
    # Strip the '=' end-of-report marker before decoding - real
    # reports have it glued onto the last group with no space
    # (e.g. "51003="), which pymetdecoder correctly rejects as not
    # matching the expected 5-character group pattern, even though
    # the group itself (without the marker) is entirely valid.
    # manual_fallback_parse has always stripped this; this path
    # never did, confirmed by a real, syntactically valid 5appp
    # pressure-tendency group being wrongly flagged as invalid.
    report_clean = str(report).replace('=', '').strip()
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
    temp, dewpoint, SLP, and wind. cloud_cover, visibility, and
    present_weather always come back None here, since reliably
    hand-parsing their group positions is much closer to
    reimplementing pymetdecoder than a fallback should attempt.
    """
    tokens = text.replace('=', '').split()
    if len(tokens) < 3:
        return None

    iw = tokens[1][-1]
    wind_unit = _WIND_UNIT_BY_IW.get(iw)

    body = tokens[3:]

    wind_dir, wind_speed = None, None
    nddff = body[1] if len(body) > 1 else None
    if nddff and len(nddff) == 5 and nddff.isdigit():
        try:
            wind_dir = int(nddff[1:3]) * 10
            wind_speed = int(nddff[3:])
        except ValueError:
            pass
    if wind_speed == 0:
        wind_dir = None
    if wind_speed is None:
        wind_unit = None

    temp, dewpoint, slp = None, None, None
    for t in body[2:]:
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

    if temp is None and slp is None:
        return None
    return {
        "temp": temp, "dewpoint": dewpoint, "slp": slp,
        "wind_dir": wind_dir, "wind_speed": wind_speed,
        "wind_speed_unit": wind_unit,
        "cloud_cover": None, "visibility": None, "present_weather": None,
    }
