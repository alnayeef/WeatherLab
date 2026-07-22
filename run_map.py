#!/usr/bin/env python3
import argparse
import sys
import matplotlib.pyplot as plt
from datetime import datetime

# Import your rock-solid pipeline functions
from weatherlab.pipeline import latest_surface_obs
from weatherlab.surface import surface_analysis

def main():
    # 1. Initialize the Command Line Argument Parser
    parser = argparse.ArgumentParser(
        description="WeatherLab Universal Surface Analysis Plotter",
        epilog="Example: python run_map.py --country Ind --hours-ago 3"
    )

    # 2. Define interactive flags the user can type in the terminal
    parser.add_argument(
        "-c", "--country",
        type=str,
        default="Bang",
        help="Ogimet country abbreviation code (e.g., Bang, Ind, USA, Euro). Default is Bang."
    )
    
    parser.add_argument(
        "-a", "--hours-ago",
        type=int,
        default=0,
        help="Look back X hours to a historical cycle. Must be a multiple of 3 (0, 3, 6, 9...). Default is 0 (latest)."
    )

    args = parser.parse_args()

    # 3. Handle data validation
    if args.hours_ago % 3 != 0:
        print(f"[-] Error: Synoptic cycles run every 3 hours. Your lookback value ({args.hours_ago}) must be a multiple of 3.")
        sys.exit(1)

    print(f"[+] Initializing Digital Atmosphere clone...")
    print(f"[+] Target Region: {args.country}")
    print(f"[+] Time Window:  {f'{args.hours_ago} hours ago' if args.hours_ago > 0 else 'Latest Live Cycle'}")
    print("--------------------------------------------------")

    try:
        # Fetching data using your universal pipeline
        # (Make sure to pass down your lookback hours down to get_raw_synop!)
        obs_df = latest_surface_obs(country=args.country, hours_ago=args.hours_ago)
        
        if obs_df.empty:
            print("[-] No data returned from server. Check your network or country code filter.")
            sys.exit(1)

        print(f"[+] Data loaded successfully! Processing {len(obs_df)} station fields...")
        print(f"[+] Generating map canvas and smoothing isobars...")
        
        fig, ax = surface_analysis(obs_df)
        
        # Give the window a professional title
        plt.gcf().canvas.manager.set_window_title(f"Surface Analysis Map - {args.country.upper()}")
        print("[+] Done! Launching interactive map viewer window...")
        plt.show()

    except Exception as e:
        print(f"[-] Critical application failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
