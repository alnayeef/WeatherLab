import re
from pymetdecoder import synop

def decode_synop(report):
    report_clean = str(report).strip()
    
    # Clean down to the starting block if AAXX is present
    if "AAXX" in report_clean:
        report_clean = report_clean[report_clean.index("AAXX"):]

    try:
        data = synop.SYNOP().decode(report_clean)
        
        # Safely extract from pymetdecoder structure
        return {
            "temp": data.get("air_temperature", {}).get("value"),
            "dewpoint": data.get("dewpoint_temperature", {}).get("value"),
            "slp": data.get("sea_level_pressure", {}).get("value"),
            "wind_dir": data.get("surface_wind", {}).get("direction", {}).get("value"),
            "wind_speed": data.get("surface_wind", {}).get("speed", {}).get("value"),
        }
    except Exception:
        # Fallback to a precise numeric group extractor
        return manual_fallback_parse(report_clean)

def manual_fallback_parse(text):
    tokens = text.replace('=', '').split()
    temp, dewpoint, slp, wind_dir, wind_speed = None, None, None, None, None

    for t in tokens:
        clean = t.replace('/', '')
        if not clean.isdigit() or len(clean) != 5:
            continue
            
        if clean.startswith('1'):  # 1sTTT Temperature
            sign = -1 if clean[1] == '1' else 1
            temp = sign * (int(clean[2:]) / 10.0)
        elif clean.startswith('2'):  # 2sTTT Dewpoint
            sign = -1 if clean[1] == '1' else 1
            dewpoint = sign * (int(clean[2:]) / 10.0)
        elif clean.startswith('4'):  # 4PPPP Sea Level Pressure
            val = int(clean[1:]) / 10.0
            slp = val + 1000.0 if val < 500.0 else val + 900.0

    # Fallback Wind extraction from standard 3rd or 4th token placement (e.g., 23008)
    for t in tokens[3:5]:
        if len(t) == 5 and t.isdigit() and not any(t.startswith(x) for x in ['1','2','3','4','5']):
            try:
                wind_dir = int(t[1:3]) * 10
                wind_speed = int(t[3:])
            except ValueError:
                pass

    if temp is None and slp is None:
        return None

    return {"temp": temp, "dewpoint": dewpoint, "slp": slp, "wind_dir": wind_dir, "wind_speed": wind_speed}
