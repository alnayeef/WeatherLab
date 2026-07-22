import numpy as np


def wind_components(speed, direction):
    """
    Convert meteorological wind direction and speed
    into u,v components.
    """

    speed = np.asarray(speed)
    direction = np.asarray(direction)

    u = -speed * np.sin(np.deg2rad(direction))
    v = -speed * np.cos(np.deg2rad(direction))

    return u, v