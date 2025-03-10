"""Aviation Utils
This script contains several functions that could be useful for aviation related operations.
Current functions are:

    * airport_lookup: Takes an icao code and returns all the info in the database about it.
    * airport_distance: Returns the distance between two airports in nautical miles.

"""


import sqlite3
import os
from . import Aviation_Math

db_path = os.path.join(os.path.dirname(__file__), '..', "Aviation_Databases", "airports.db")

def airport_lookup(airport: str):
    """Takes an icao code and returns all the info in the database about it.

    Parameters
    ----------
    lat1 : str
        ICAO code for the airport we want to search for.

    Returns
    ----------
    tuple
        A tuple containing all the info about the airport.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    airport = airport.upper()

    sql = "SELECT * FROM airports WHERE ident = ?"
    cursor.execute(sql, (airport,))
    airport = cursor.fetchall()
    db.close()
    if airport == []:
        return False
    else:
        return airport

def airport_distance(first_airport: str, second_airport: str):
    """Returns the distance between two airports in nautical miles.

    Parameters
    ----------
    first_airport : str
        ICAO code for the first airport.
    second_airport : str
        ICAO code for the second airport.

    Returns
    ----------
    float
        The distance between the two airports in nm.
    """
    first_airport = first_airport.upper()
    second_airport = second_airport.upper()
        
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
        
    sql = "SELECT * FROM airports WHERE ident = ?"
    cursor.execute(sql, (first_airport,))
    first_airport = cursor.fetchall()
    if first_airport == []:
        return False
    first_airport_cords = (float(first_airport[0][4]), float(first_airport[0][5]))

    cursor.execute(sql, (second_airport,))
    second_airport = cursor.fetchall()
    if second_airport == []:
        return False
    second_airport_cords = (float(second_airport[0][4]), float(second_airport[0][5]))

    distance = Aviation_Math.great_circle_distance(first_airport_cords[0], first_airport_cords[1], second_airport_cords[0], second_airport_cords[1])

    distance = Aviation_Math.km_to_nm(distance)

    return distance

def random_regional_flight():
    """Returns a random flight that takes place inside a country"""
    pass