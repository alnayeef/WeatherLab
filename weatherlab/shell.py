"""Interactive GrADS-style shell. Commands are plain words, not
terse abbreviations - "set country Bangladesh", not "d slp" - so
nothing needs to be memorized up front."""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
try:
    import readline  # enables up/down history and line-editing for input()
except ImportError:
    pass  # not available on Windows without pyreadline3 - shell still works, just without history

from datetime import datetime, UTC
from importlib.metadata import version

from .countries import resolve_country
from .pipeline import surface_obs
from .interpolate import pressure_field
from .plotting import create_map, plot_isobars, plot_station_model

VERSION = version("weatherlab")

HELP_TEXT = """\
Commands:
  set country <name>   Set the country to plot (e.g. set country Bangladesh)
  set time <time>      Set the target hour, UTC, as YYYY-MM-DD HH:MM
  show                 Show the currently set country and time
  plot                 Draw the surface chart for the current country/time
  help                 Show this message
  exit                 Quit
"""


class ShellState:
    def __init__(self):
        self.country = None
        self.time = None
        self.fig = None
        self.ax = None


def _blank_window(state):
    """A window with nothing plotted yet - GrADS itself opens one
    immediately on startup, before any data command has been given."""
    fig, ax = create_map(obs=None)
    fig.canvas.manager.set_window_title(f"WeatherLab {VERSION}")
    plt.show(block=False)
    fig.canvas.draw()
    fig.canvas.flush_events()
    state.fig = fig
    state.ax = ax


def _draw(state):
    """Redraws onto the SAME axes/window each time (create_map with
    ax= clears and reconfigures it) rather than opening a new one -
    confirmed directly that this works correctly on a cartopy axes,
    including going from the blank startup state to a real map."""
    target = datetime.strptime(state.time, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
    obs = surface_obs(state.country, target)
    if obs.empty:
        print("No stations decoded for this country/time - nothing to plot.")
        return

    create_map(obs, ax=state.ax)
    LON, LAT, SLP = pressure_field(obs)
    plot_isobars(state.ax, LON, LAT, SLP)
    plot_station_model(state.ax, obs)
    state.fig.canvas.manager.set_window_title(f"WeatherLab {VERSION} - {state.country} {state.time}")
    state.fig.canvas.draw()
    state.fig.canvas.flush_events()


def handle_command(state, line):
    parts = line.strip().split(maxsplit=2)
    if not parts:
        return True
    verb = parts[0].lower()

    if verb in ("exit", "quit"):
        return False
    if verb == "help":
        print(HELP_TEXT)
        return True
    if verb == "show":
        print(f"country: {state.country or '(not set)'}")
        print(f"time: {state.time or '(not set)'}")
        return True
    if verb == "set" and len(parts) == 3 and parts[1].lower() == "country":
        name = parts[2]
        try:
            resolve_country(name)
        except LookupError:
            print(f"'{name}' isn't a recognized country name.")
            return True
        state.country = name
        print(f"country set to {name}")
        return True
    if verb == "set" and len(parts) == 3 and parts[1].lower() == "time":
        value = parts[2]
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"'{value}' isn't a valid time - use YYYY-MM-DD HH:MM.")
            return True
        state.time = value
        print(f"time set to {value}")
        return True
    if verb == "plot":
        missing = [n for n, v in [("country", state.country), ("time", state.time)] if v is None]
        if missing:
            print(f"Can't plot yet - not set: {', '.join(missing)}")
            return True
        _draw(state)
        return True

    print(f"Unrecognized command: {line!r}. Type 'help' for a list.")
    return True


def run():
    print(f"WeatherLab {VERSION}")
    print("Created and maintained by Naif.")
    print("Type 'help' for commands, 'exit' to quit.")
    state = ShellState()
    _blank_window(state)
    while True:
        try:
            line = input("weatherlab> ")
        except EOFError:
            break
        if not handle_command(state, line):
            break
    if state.fig is not None:
        plt.close(state.fig)
