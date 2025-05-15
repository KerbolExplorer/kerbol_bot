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

def airport_distance(coordinates1, coordinates2):
    """Returns the distance between two airports in nautical miles.

    Parameters
    ----------
    coordinates1 : tuple
        The coordinates for the first airport (lat, long).
    coordinates2 : tuple
        The coordinates for the second airport (lat, long).

    Returns
    ----------
    float
        The distance between the two airports in nm.
    """

    distance = Aviation_Math.great_circle_distance(float(coordinates1[0]), float(coordinates1[1]), float(coordinates2[0]), float(coordinates2[1]))

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

def valid_icao(airport:str):
    """Checks if an airport has a valid icao code ()"""
    if len(airport) > 4:
        return False
    else:
        return True


def random_flight(country:str, international:bool = False, departing_airport:str = None, arrival_airport:str = None, min_distance = None, max_distance = None, type = "small_airport"):
    """Returns a random flight

    Parameters
    ----------
    country: ISO code of the country.
    international: If the flight is internation (not implemented).
    departing_airport: The airport you want to depart from.
    arrival_airport: The airport you arrive at.
    min_distance: The minimum distance of the flight.
    max_distance: The max distance of the flight.

    Returns
    ----------
    None: If there's no airport in the country given.
    1: If there is only 1 airport in this country.
    2: If the departing airport is not valid.
    3: If the arrival airport is not valid
    Tuple
        A tuple containing the information of the flight.
    """
    import random

    country = country.upper()
    airport_db = sqlite3.connect(db_path)
    cursor = airport_db.cursor()

    sql = "SELECT name, latitude_deg, longitude_deg, ident FROM airports WHERE iso_country = ? AND type != 'heliport' AND type = ?"
    cursor.execute(sql, (country, type))
    all_airports = cursor.fetchall()

    if not all_airports:
        cursor.close()
        airport_db.close()
        return None
    elif len(all_airports) == 1:
        cursor.close()
        airport_db.close()
        return 1
    
    if min_distance is None:
        min_distance = 0
    if max_distance is None:
        max_distance = 9999
    
    if max_distance < min_distance:
        cursor.close()
        airport_db.close()
        return None
    
    departure_locked = False
    arrival_locked = False

    if departing_airport is not None:
        departing_airport = airport_lookup(departing_airport)
        departure_locked = True
        if departing_airport == False:
            cursor.close()
            airport_db.close()
            return 2

        departing_cords = (departing_airport[0][4], departing_airport[0][5])
        departing_airport = (departing_airport[0][3], departing_airport[0][1])

    if arrival_airport is not None:
        arrival_airport = airport_lookup(arrival_airport)
        arrival_locked = True
        if arrival_airport == False:
            cursor.close()
            airport_db.close()
            return 3
        arrival_cords = (arrival_airport[0][4], arrival_airport[0][5])
        arrival_airport = (arrival_airport[0][3], arrival_airport[0][1])
    
    attempts = 20
    total_attempts = 0
    while attempts > 0:
        if not departure_locked:
            dep = random.choice(all_airports)
            departing_cords = (dep[1], dep[2])
            departing_airport = (dep[0], dep[3])
        
        if not arrival_locked:
            arrival = random.choice(all_airports)
            arrival_cords = (arrival[1], arrival[2])
            arrival_airport = (arrival[0], arrival[3])

        if valid_icao(departing_airport[1]) == False:
            attempts += 1
            total_attempts += 1
            continue
        if valid_icao(arrival_airport[1]) == False:
            attempts += 1
            total_attempts += 1
            continue

        distance = airport_distance(departing_cords, arrival_cords)

        if distance < min_distance or distance > max_distance:
            attempts -= 1
            if attempts == 0:
                min_distance = max(0, min_distance - 25)
                max_distance += 25
                attempts = 20
            total_attempts += 1
        else:
            break
        if total_attempts == 100:
            cursor.close()
            airport_db.close()
            return None

    if distance < min_distance or distance > max_distance:
        cursor.close()
        airport_db.close()
        return None
    
    cursor.close()
    airport_db.close()
    return (departing_airport, arrival_airport, distance)