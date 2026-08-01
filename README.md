# WeatherLab

A GrADS-style CLI for decoding SYNOP weather reports and drawing surface weather charts — built as an open alternative to Digital Atmosphere.

See [ROADMAP.md](ROADMAP.md) for exactly what's built so far and what's still ahead, tracked feature-by-feature against Digital Atmosphere.

## What it does

WeatherLab fetches real SYNOP surface observations for any country and a specific hour, decodes them, and draws a full traditional surface weather chart in a live window: temperature, dewpoint, sea-level pressure, wind barbs, cloud cover, present weather, and visibility at each station, with isobars analyzed across the whole region.

## Requirements

- Python 3.11 or newer
- A system Tk installation, for the plotting window:
  - Fedora: `sudo dnf install python3.13-tkinter` (substitute whichever Python version you're using)
  - Other distributions typically call this package `python3-tk` — not yet confirmed on anything but Fedora

## Installation

```
git clone https://github.com/alnayeef/WeatherLab.git
cd WeatherLab
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

A virtual environment isn't strictly required, but keeps WeatherLab's dependencies separate from anything else installed on your system.

## Usage

### Interactive shell

Run `weatherlab` with no arguments to open a live plotting window and an interactive prompt — this is the primary way to use WeatherLab, closer to GrADS's own style than a single one-shot command.

```
$ weatherlab
WeatherLab 0.1.0
Created and maintained by Naif.
Type 'help' for commands, 'exit' to quit.
weatherlab> set country Bangladesh
country set to Bangladesh
weatherlab> set time 2026-07-23 21:00
time set to 2026-07-23 21:00
weatherlab> plot
weatherlab> save
Saved Bangladesh_2026-07-23_2100.png
weatherlab> exit
```

The window opens immediately at startup, blank, before any command is given, and stays open across every `plot` call until you `exit`. Command history works with the up and down arrow keys, the same as a regular shell.

**Commands:**

| Command | Description | Example |
|---|---|---|
| `set country <name>` | Set the country to plot. Accepts common variations, not just official names. | `set country Bangladesh`, `set country US` |
| `set time <time>` | Set the target synoptic hour, in UTC, as `YYYY-MM-DD HH:MM`. | `set time 2026-07-23 21:00` |
| `set min-radius <value>` | Minimum degrees required between two plotted stations. Stations closer together than this to an already-kept one are skipped, to keep dense clusters readable. Defaults to `0.3`. Set to `0` to draw every decoded station regardless of crowding. | `set min-radius 0`, `set min-radius 1.5` |
| `show` | Print the currently set country, time, and min-radius. | `show` |
| `plot` | Draw the chart for the currently set country and time. Requires both to be set first. | `plot` |
| `save [filename]` | Save the currently displayed chart as a PNG. Uses `<country>_<time>.png` if no filename is given. Requires `plot` to have been run first. | `save`, `save my_chart.png` |
| `help` | Show the list of commands. | `help` |
| `exit` | Close the window and quit. | `exit` |

### One-shot command

To draw a single chart directly, without opening the interactive shell:

```
weatherlab surface --country Bangladesh --time "2026-07-23 21:00"
```

This opens the same live window as the shell's `plot` command. The window stays open until you close it, at which point the command finishes.

**Options:**

| Option | Description | Example |
|---|---|---|
| `--country` | Required. Country name, same rules as `set country` above. | `--country Bangladesh` |
| `--time` | Required. Target synoptic hour, UTC, as `YYYY-MM-DD HH:MM`. | `--time "2026-07-23 21:00"` |
| `--save` | Also write the chart to a PNG in the current directory, in addition to showing it. Off by default. | `--save` |
| `--min-radius` | Same meaning as the shell's `set min-radius`. Defaults to `0.3`. | `--min-radius 0` |

Full example, saving a file and drawing every station with no thinning:

```
weatherlab surface --country Bangladesh --time "2026-07-23 21:00" --save --min-radius 0
```

## Data sources

- Station reports: [Ogimet](https://www.ogimet.com)
- Station metadata: [WMO OSCAR/Surface](https://oscar.wmo.int/surface/)

## License

MIT — see [LICENSE](LICENSE).

Created and maintained by Naif.
