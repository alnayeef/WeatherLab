"""Command-line interface for WeatherLab."""

import matplotlib
matplotlib.use("TkAgg")  # must be set before any import below touches pyplot

from datetime import datetime, UTC

import typer

from .pipeline import surface_obs
from .interpolate import pressure_field
from .plotting import create_map, plot_isobars, plot_station_model
from . import shell as shell_module

app = typer.Typer()


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        shell_module.run()


@app.command()
def surface(
    country: str = typer.Option(..., help="Country name, e.g. 'Bangladesh'"),
    time: str = typer.Option(..., help="Target synoptic hour, UTC, as 'YYYY-MM-DD HH:MM'"),
    min_radius: float = typer.Option(
        0.3,
        help="Minimum degrees between plotted stations, to reduce overlap in "
             "dense clusters. Set to 0 to draw every station regardless of crowding.",
    ),
):
    """Draw a surface weather chart for one country and one synoptic hour."""
    target = datetime.strptime(time, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)

    obs = surface_obs(country, target)
    if obs.empty:
        typer.echo("No stations decoded for this country/time - nothing to plot.")
        raise typer.Exit(code=1)

    fig, ax = create_map(obs)
    LON, LAT, SLP = pressure_field(obs)
    plot_isobars(ax, LON, LAT, SLP)
    plot_station_model(ax, obs, min_radius=min_radius if min_radius > 0 else None)

    output = f"{country.replace(' ', '_')}_{time.replace(' ', '_').replace(':', '')}.png"
    fig.savefig(output, dpi=300)
    typer.echo(f"Saved {output}")


def main():
    app()


if __name__ == "__main__":
    main()
