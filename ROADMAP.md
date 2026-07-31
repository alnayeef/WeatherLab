# WeatherLab vs. Digital Atmosphere

A running, honest comparison — updated as each item actually moves.

## Data sources
| Feature | DA | WeatherLab |
|---|---|---|
| SYNOP (surface) | Yes | **Done** — any country, one target hour, via Ogimet |
| METAR | Yes | Not started |
| Ship SYNOP, AIREP | Yes | Not started |
| Upper-air (RAOB/TEMP) | Yes | Not started (planned, separate track) |
| Offline replay of saved/"canned" data | Yes | Not started — WeatherLab always fetches live |
| Scheduled automatic refresh | Yes | Not started |

## Region & stations
| Feature | DA | WeatherLab |
|---|---|---|
| Select by country | No (DA is extent-based) | **Done** |
| Select by custom lat/lon box | Yes | Not started — current biggest gap |
| Station database | ~30,000 stations, user-editable, bundled | **Done**, differently: any country fetched live from WMO OSCAR/Surface, cached locally |
| Manual data correction / QC | Yes | Not started |

## Station model
| Feature | DA | WeatherLab |
|---|---|---|
| Temp, dewpoint, SLP, wind barbs | Yes | **Done** |
| Cloud cover, present weather, visibility | Yes | **Done** |
| Flight-category coloring — VFR=green (ceiling >3000ft, vis >5mi), MVFR=blue (1000-3000ft, 3-5mi), IFR=red (500-1000ft, 1-3mi), LIFR=magenta (<500ft, <1mi) | Yes | Not started, but close — visibility already decoded; only cloud-base height still needs pulling from pymetdecoder |
| Computerized-station marker | Yes | Not started, minor |

## Surface analysis
| Feature | DA | WeatherLab |
|---|---|---|
| SLP isobars | Yes | **Done** — fixed 4 hPa intervals, smoothed |
| Frontal depiction | Yes | Not started |
| Vorticity / divergence / advection | Yes | Not started — advanced, later |

## Upper air
| Feature | DA | WeatherLab |
|---|---|---|
| Mandatory pressure levels (850, 500 hPa, etc.) | Yes | Not started |

## Analysis menu
| Feature | DA | WeatherLab |
|---|---|---|
| Temperature / dewpoint contours | Yes | Not started |
| Wind: barbs | Yes | **Done** |
| Wind: vectors, streamlines | Yes | Not started |
| Moisture (RH, mixing ratio) | Yes | Not started — not decoded yet |
| Precipitation (1h/3h/6h/12h/24h) | Yes | Not started — not decoded yet |
| NWS watches/warnings overlay | Yes | Not started |

## Plotting workflow
| Feature | DA | WeatherLab |
|---|---|---|
| Selective/modular plotting — draw one field or layer at a time (e.g. just wind barbs, or just isobars) rather than everything at once | Yes — each analysis chosen individually via menus | Not started — the whole station model and isobar layer are currently fixed, all-or-nothing bundles, not independently toggleable pieces |

## Interface
| Feature | DA | WeatherLab |
|---|---|---|
| GUI, point-and-click | Yes | No — not the design goal |
| Scriptable, plain-language CLI shell | No | **Done** — a real advantage over DA: repeatable and automatable in a way point-and-click isn't |

*Last updated: interactive shell, command history, MIT license.*
