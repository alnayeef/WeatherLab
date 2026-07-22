import re
from datetime import datetime, UTC, timedelta
from io import StringIO
import pandas as pd
import requests

def get_raw_synop(country="Bang", hours_ago=0): # 1. Added hours_ago here
    """
    Download the latest SYNOP reports from Ogimet.
    """
    # 2. Subtract the user's requested hours from the current time
    now = datetime.now(UTC) - timedelta(hours=hours_ago)
    
    # 3. Calculate the closest 3-hour synoptic cycle hour based on that past time
    cycle_hour = (now.hour // 3) * 3
    
    # The rest of your code stays exactly the same...
    begin = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)
    target_times = [begin, begin - timedelta(hours=3)]
    
    for target_time in target_times:
        url = (
            "https://www.ogimet.com/cgi-bin/getsynop"
            f"?begin={target_time:%Y%m%d%H%M}"
            f"&end={target_time:%Y%m%d%H%M}"
            f"&state={country}"
            "&lang=eng"
        )
        
        print(f"Trying cycle time: {target_time:%Y-%m-%d %H:%M} UTC...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # --- TINY STEP: Scan every single line of the page response directly ---
            clean_lines = []
            for line in response.text.splitlines():
                line = line.strip()
                
                # If the line contains exactly 6 commas and doesn't start with an HTML tag bracket, it's our data
                if line and line.count(",") == 6 and not line.startswith("<"):
                    clean_lines.append(line)
            
            if clean_lines:
                print(f"-> Success! Safely isolated {len(clean_lines)} data lines for cycle: {target_time:%Y-%m-%d %H:%M} UTC")
                data_stream = "\n".join(clean_lines)
                
                columns = ["WMOIND", "YEAR", "MONTH", "DAY", "HOUR", "MIN", "REPORT"]
                
                df = pd.read_csv(
                    StringIO(data_stream),
                    sep=",",
                    names=columns,
                    engine="python"
                )
                return df
                
        except Exception as e:
            print(f"Skipping window due to error: {e}")
            continue
            
    return pd.DataFrame(columns=["WMOIND", "YEAR", "MONTH", "DAY", "HOUR", "MIN", "REPORT"])
