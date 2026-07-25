"""Decode raw SYNOP reports using pymetdecoder, with a best-effort
manual fallback for reports pymetdecoder can't parse."""

from pymetdecoder import synop


def decode_synop(report):
    report_clean = str(report).strip()
    if "AAXX" in report_clean:
        report_clean = report_clean[report_clean.index("AAXX"):]

    try:
        data = synop.SYNOP().decode(report_clean)
        wind_speed = data.get("surface_wind", {}).get("speed", {})
        return {
            "temp": data.get("air_temperature", {}).get("value"),
            "dewpoint": data.get("dewpoint_temperature", {}).get("value"),
            "slp": data.get("sea_level_pressure", {}).get("value"),
            "wind_dir": data.get("surface_wind", {}).get("direction", {}).get("value"),
            "wind_speed": wind_speed.get("value"),
            "wind_speed_unit": wind_speed.get("unit"),
            "cloud_cover": data.get("cloud_cover", {}).get("value"),
            "visibility": data.get("visibility", {}).get("value"),
            "present_weather": data.get("present_weather", {}).get("value"),
        }
    except Exception:
        return manual_fallback_parse(report_clean)


def manual_fallback_parse(text):
    """
    Best-effort parse for reports pymetdecoder can't handle. Only
    recovers temp, dewpoint, SLP, and wind - cloud_cover, visibility,
    present_weather, and wind_speed_unit always come back None here,
    since reliably hand-parsing their group positions is much closer
    to reimplementing pymetdecoder than a fallback should attempt.
    """
    tokens = text.replace('=', '').split()
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
    # iRixhVV then Nddff, in that order - Nddff (the real wind group)
    # is evaluated last, so it always wins if both happen to qualify.
    for t in body[:2]:
        if len(t) == 5 and t.isdigit():
            try:
                wind_dir = int(t[1:3]) * 10
                wind_speed = int(t[3:])
            except ValueError:
                pass
    if wind_speed == 0:
        # WMO convention: calm is coded as direction 00, meaning "no
        # direction", not "from the north". Matches pymetdecoder's own
        # behavior on the primary path above.
        wind_dir = None

    if temp is None and slp is None:
        return None
    return {
        "temp": temp, "dewpoint": dewpoint, "slp": slp,
        "wind_dir": wind_dir, "wind_speed": wind_speed,
        "wind_speed_unit": None,
        "cloud_cover": None, "visibility": None, "present_weather": None,
    }
