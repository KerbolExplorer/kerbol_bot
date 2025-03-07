"""Aviation Math
This script contains several functions that could be useful for aviation related calculations.
Current functions are:

    * great_circle_distance: Takes two sets of coordinates and returns the distance between them in km.
    * km_to_nm: Takes a value in km and returns it in nm.

"""

import math


def great_circle_distance(lat1, lon1, lat2, lon2) -> float:
    """Takes two sets of coordinates and returns the distance between them in km.

    Parameters
    ----------
    lat1 : float
        Latitude of the first point.
    lon1 : float
        Longitude of the first point.
    lat2: float
        Latitude of the second point.
    lon2: float
        Longitude of the second point.

    Returns
    ----------
    float
        The great-circle distance between the two points in kilometers.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    d = 2 * 6371 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2 +
        math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2 
    ))

    return d

def km_to_nm(kilometers):
    """Takes a value in km and returns it in nm.

    Parameters
    ----------
    kilometers: float
        The value to convert
    
    Returns
    ----------
        The value converted to nm
    """
    return kilometers * 0.5399568035