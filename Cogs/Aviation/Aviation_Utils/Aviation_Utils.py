"""Aviation Utils
This script contains several functions that could be useful for aviation related operations.
Current functions are:

    * airport_lookup: Takes an icao code and returns all the info in the database about it.
    * airport_distance: Returns the distance between two airports in nautical miles.
    * get_metar: Returns the metar for an airport.
    * get_current_zulu: Returns the current zulu time.

"""


import sqlite3
import os
import requests
from datetime import datetime, timezone
from . import Aviation_Math

db_path = os.path.join(os.path.dirname(__file__), '..', "Aviation_Databases", "airports.db")

def airport_lookup(airport: str):
    """Takes an icao code and returns all the info in the database about it.

    Parameters
    ----------
    airport : str
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

def get_metar(icao_code: str, raw_only = True):
    """Returns the current metar for an airport.

    Parameters
    ----------
    icao_code : str
        ICAO code for the airport.
    raw_only : boolean
        Decides if we only return a string with the raw data, or a dictionary with all the data.

    Returns
    ----------
    string
        Returns the raw metar for the airport.
    boolean
        Returns False if there was an issue getting the metar.
    None
        Returns None if there's no metar.
    """
    icao_code = icao_code.upper()
    url = "https://aviationweather.gov/api/data/metar"
    params = {
        "ids": icao_code,
        "format": "json",
        "taf": "false",
        "mostRecent": "true",
        "hours": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        metars = response.json()

        if not metars:
            return None
        
        metar = metars[0]
        if raw_only:
            return metar["rawOb"]
        else:
            return metar
    except requests.RequestException:
        return False
    except ValueError:
        return False

def get_current_zulu():
    """Returns the current zulu time.

    Returns
    ----------
    Integer
        The current zulu time.
    """
    current_time = datetime.now(timezone.utc)
    current_time = int(current_time.strftime("%H%M"))
    return current_time


def random_flight(country:str, international:bool = False, departing_airport:str = None, arrival_airport:str = None, min_distance:int = 0, max_distance:int = 9999):
    """Returns a random flight

    Parameters
    ----------
    country: ISO code of the country.
    international: If the flight is internation (not implemented).
    departing_airport: The airport you want to depart from.
    arrival_airport: The airport you arrive at.
    min_distance: The minimum distance of the flight (not implemented).
    max_distance: The max distance of the flight (not implemented).

    Returns
    ----------
    None: If there's no airport in the country given.
    1: If there is only 1 airport in this country.
    2: If the departing airport is not valid.
    3: If the arrival airport is not valid
    Tuple
        A tuple containing the information of the flight.
    """
    
    country = country.upper()
    airport_db = sqlite3.connect(db_path)
    cursor = airport_db.cursor()

    sql = "SELECT name, latitude_deg, longitude_deg, ident FROM airports WHERE iso_country = ? AND type != 'heliport' AND type != 'closed' ORDER BY RANDOM() LIMIT 20"
    cursor.execute(sql, (country,))
    airport_choices = cursor.fetchall()
    airport_db.close()

    if not airport_choices:
        return None
    elif len(airport_choices) == 1:
        return 1
    
    if departing_airport == None:
        departing_airport = (airport_choices[0][0], airport_choices[0][3])
    else:
        departing_airport = airport_lookup(departing_airport)

        if departing_airport == False:
            return 2

        departing_airport = (departing_airport[0][3], departing_airport[0][1])

    if arrival_airport == None:
        arrival_airport = (airport_choices[1][0], airport_choices[1][3])
    else:
        arrival_airport = airport_lookup(arrival_airport)

        if arrival_airport == False:
            return 3

        arrival_airport = (arrival_airport[0][3], arrival_airport[0][1])

    distance = airport_distance(departing_airport[1], arrival_airport[1])

    return (departing_airport, arrival_airport, distance)