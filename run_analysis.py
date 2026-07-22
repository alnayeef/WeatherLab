import os
import matplotlib.pyplot as plt
from weatherlab.pipeline import latest_surface_obs
from weatherlab.surface import surface_analysis

def main():
    print("--- Starting WeatherLab Surface Analysis Workstation ---")
    
    # 1. Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # 2. Fetch, decode, and merge station properties from Ogimet
    print("Ingesting data from Ogimet (this might take a few seconds)...")
    try:
        obs_df = latest_surface_obs()
    except Exception as e:
        print(f"Extraction failed: {e}")
        return

    if obs_df.empty:
        print("Warning: Retrieved an empty table. Check your connection or the UTC hour cycle.")
        return
        
    print(f"Successfully processed {len(obs_df)} station reports.")
    print(obs_df[["wmo", "temp", "dewpoint", "slp"]].head())

    # 3. Pass data matrix to the mapping environment
    print("\nInterpolating pressure fields and drawing maps...")
    fig, ax = surface_analysis(obs_df)
    
    # 4. Save file locally
    output_filename = "bangladesh_surface_analysis.png"
    plt.title(f"WeatherLab Surface Analysis Map\nGenerated: {plt.datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC", fontsize=10)
    
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"Success! Weather chart saved to: {output_filename}")
    plt.close()

if __name__ == "__main__":
    main()
