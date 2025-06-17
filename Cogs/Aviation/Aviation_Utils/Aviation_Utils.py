"""Aviation Utils
This script contains several functions that could be useful for aviation related operations.
Current functions are:

    * airport_lookup: Takes an icao code and returns all the info in the database about it.
    * airport_distance: Returns the distance between two airports in nautical miles.
    * get_metar: Returns the metar for an airport.
    * get_current_zulu: Returns the current zulu time.
    * registration_creator  creates a random registration.

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
    """Checks if an airport has a valid icao code (At or below 4 letters, so stuff like GCLP or L53).


    Parameters
    ----------
    String
        The icao code we want to check.
    
    Returns
    ----------
    Boolean
        True if it's valid, False if it's not.
    """
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
        departing_cords = (departing_airport[0][4], departing_airport[0][5])
        if departing_airport == False:
            cursor.close()
            airport_db.close()
            return 2

        departing_cords = (departing_airport[0][4], departing_airport[0][5])
        departing_airport = (departing_airport[0][3], departing_airport[0][1])

    if arrival_airport is not None:
        arrival_airport = airport_lookup(arrival_airport)
        arrival_locked = True
        arrival_cords = (arrival_airport[0][4], arrival_airport[0][5])
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


def registration_creator(iso_code, type = None):
    """Creates a random registration.


    Parameters
    ----------
    String
        Iso code of the country of the registration.
    
    Returns
    ----------
    String
        A random registration.
    """
    import string
    import random

    country_prefixes = {
    "AF": ["YA"],
    "AL": ["ZA"],
    "DZ": ["7T"],
    "AO": ["D2"],
    "AG": ["V2"],
    "AR": ["LV", "LQ"],
    "AM": ["EK"],
    "AW": ["P4"],
    "AU": ["VH"],
    "AT": ["OE"],
    "AZ": ["4K"],
    "BS": ["C6"],
    "BH": ["A9C"],
    "BD": ["S2"],
    "BB": ["8P"],
    "BY": ["EW"],
    "BE": ["OO"],
    "BZ": ["V3"],
    "BT": ["A5"],
    "BO": ["CP"],
    "BA": ["E7"],
    "BW": ["A2"],
    "BR": ["PP", "PR", "PS", "PT"],
    "BN": ["V8"],
    "BG": ["LZ"],
    "KH": ["XU"],
    "CM": ["TJ"],
    "CA": ["C", "CF"],
    "CV": ["D4"],
    "KY": ["VP-C", "VR-C"],
    "CL": ["CC"],
    "CN": ["B"],
    "CO": ["HK", "HJ"],
    "KM": ["D6"],
    "CG": ["TN"],
    "CD": ["9Q"],
    "CR": ["TI"],
    "HR": ["9A"],
    "CU": ["CU"],
    "CY": ["5B"],
    "CZ": ["OK"],
    "DK": ["OY"],
    "DJ": ["J2"],
    "DM": ["J7"],
    "DO": ["HI"],
    "EC": ["HC"],
    "EG": ["SU"],
    "SV": ["YS"],
    "GQ": ["3C"],
    "ER": ["E3"],
    "EE": ["ES"],
    "ET": ["ET"],
    "FK": ["VP-F"],
    "FI": ["OH"],
    "FR": ["F"],
    "GA": ["TR"],
    "GM": ["C5"],
    "GE": ["4L"],
    "DE": ["D"],
    "GH": ["9G"],
    "GR": ["SX"],
    "GD": ["J3"],
    "GT": ["TG"],
    "GN": ["3X"],
    "GW": ["J5"],
    "GY": ["8R"],
    "HT": ["HH"],
    "HN": ["HR"],
    "HU": ["HA"],
    "IS": ["TF"],
    "IN": ["VT"],
    "ID": ["PK"],
    "IR": ["EP"],
    "IQ": ["YI"],
    "IE": ["EI", "EJ"],
    "IM": ["M"],
    "IL": ["4X"],
    "IT": ["I"],
    "JM": ["6Y"],
    "JP": ["JA"],
    "JO": ["JY"],
    "KZ": ["UP", "UN"],
    "KE": ["5Y"],
    "KW": ["9K"],
    "LA": ["RDPL"],
    "LV": ["YL"],
    "LB": ["OD"],
    "LR": ["EL"],
    "LY": ["5A"],
    "LT": ["LY"],
    "LU": ["LX"],
    "MO": ["CR-M"],
    "MK": ["Z3"],
    "MG": ["5R"],
    "MW": ["7Q"],
    "MY": ["9M"],
    "MV": ["8Q"],
    "ML": ["TZ"],
    "MT": ["9H"],
    "MH": ["V7"],
    "MR": ["5T"],
    "MU": ["3B"],
    "MX": ["XA", "XB", "XC"],
    "FM": ["V6"],
    "MD": ["ER"],
    "MC": ["3A"],
    "MN": ["JU"],
    "ME": ["4O"],
    "MS": ["VP-M"],
    "MA": ["CN"],
    "MZ": ["C9"],
    "MM": ["XY", "XZ"],
    "NA": ["V5"],
    "NR": ["C2"],
    "NP": ["9N"],
    "NL": ["PH"],
    "AN": ["PJ"],
    "NZ": ["ZK", "ZL", "ZM"],
    "NI": ["YN"],
    "NE": ["5U"],
    "NG": ["5N"],
    "NO": ["LN"],
    "OM": ["A40"],
    "PK": ["AP"],
    "PA": ["HP"],
    "PG": ["P2"],
    "PY": ["ZP"],
    "PE": ["OB"],
    "PH": ["RP"],
    "PL": ["SP"],
    "PT": ["CS"],
    "QA": ["A7"],
    "RO": ["YR"],
    "RU": ["RA"],
    "KN": ["V4"],
    "LC": ["J6"],
    "VC": ["J8"],
    "WS": ["5W"],
    "SM": ["T7"],
    "SA": ["HZ"],
    "SN": ["6V", "6W"],
    "RS": ["YU"],
    "SC": ["S7"],
    "SL": ["9L"],
    "SG": ["9V"],
    "SK": ["OM"],
    "SI": ["S5"],
    "SB": ["H4"],
    "SO": ["6O"],
    "ZA": ["ZS", "ZT", "ZU"],
    "KR": ["HL"],
    "ES": ["EC"],
    "LK": ["4R"],
    "SD": ["ST"],
    "SR": ["PZ"],
    "SE": ["SE"],
    "CH": ["HB"],
    "SY": ["YK"],
    "TW": ["B"],
    "TZ": ["5H"],
    "TH": ["HS"],
    "TG": ["5V"],
    "TN": ["TS"],
    "TR": ["TC"],
    "TM": ["EZ"],
    "UG": ["5X"],
    "UA": ["UR"],
    "AE": ["A6"],
    "GB": ["G"],
    "US": ["N"],
    "UY": ["CX"],
    "UZ": ["UK"],
    "VU": ["YJ"],
    "VA": ["HV"],
    "VE": ["YV"],
    "VN": ["VN"],
    "YE": ["7O"],
    "ZM": ["9J"],
    "ZW": ["Z"]
}

    def random_letters(length):
        return ''.join(random.choices(string.ascii_uppercase, k=length))
    
    def random_numbers(length):
        return ''.join(random.choices(string.digits, k=length))

    prefix = country_prefixes[iso_code]

    if len(prefix) > 1:
        prefix = random.choice(prefix)
    else:
        prefix = prefix[0]
    
    if iso_code == "US":
        choices = [
            prefix + "-" + random_numbers(5),
            prefix + "-" + random_numbers(3) + random_letters(2),
            prefix + "-" + random_numbers(1) + random_letters(3),
        ]
        registration = random.choice(choices)
    elif iso_code == "CN":
        registration = prefix + "-" + random_numbers(4)
    elif iso_code == "JA":
        registration = prefix + "-" + random_numbers(4)
    elif iso_code == "KR":
        registration = prefix + random_numbers(4)
    elif iso_code == "RU":
        registration = prefix + "-" + random_numbers(5)
    else:
        registration = prefix + "-" + random_letters(4)

    return registration

if __name__ == "__main__":
    while True:
        code = input("Insert country code: ")
        print(registration_creator(code))