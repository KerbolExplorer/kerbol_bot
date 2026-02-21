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
import aiohttp
from dataclasses import dataclass
SIMBRIEF_URL = "https://www.simbrief.com/api/xml.fetcher.php"
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

def get_navaid(navaid):
    """ONLY WORKS FOR US Returns information belonging to a navaid(VOR, DME, Fix, etc).

    Parameters
    ----------
    navaid : str
        The ID of the navaid

    Returns
    ----------
    dict
        All information belonging to the navaid.
    False
        On request error.
    None
        If not found.
    """
    navaid = navaid.upper()
    url = "https://aviationweather.gov/api/data/navaid"
    params = {
        "ids":navaid,
        "format":"json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        navaids = response.json()

        if not navaids:
            return None
        
        return navaids

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

# Grab needed information before sending
@dataclass
class FlightPlan:
    """
    A class used to represent a Simbrief flightplan
    ...
    Attributes
    ----------
    icao_airline : str
        icao code for the airline
    flight_number : str
        Flight number
    aircraft : tuple
        A tuple containing the information of the aircraft (Type, registration)
    origin : str
        icao code for the departing airport
    destination : str
        icao code for the arrival airport
    alternate : str
        icao code for the alternate airport
    to_alternate : str
        icao code for take off alternate airport, defaults to None
    rte_alternate :str
        icao code for route alternate airport, defaults to None
    departure_time : str
        Take off time
    arrival_time : str
        Arrival time
    block_time : str
        Block time for the flight
    route : str
        The Route of the flight
    alt_route : str
        Route for the alternate airport
    initial_alt : str
        Initial cruise altitude
    cruise_mach : float
        Cruise mach for the flight
    cost_index : int
        Cost index for the flight
    stepclimbs : str
        Step climbs for the flight
    wind_dir : str
        Average wind direction
    wind_speed : str
        Avarage wind speed
    origin_metar: str
        Metar for the departure airport
    origin_cat: str
        Weather category for the departure airport
    destination_metar: str
        Metar for the arrival airport
    destination_cat: str
        Weather category for the arrival airport
    passengers : int
        Passenger count
    cargo : int
        Cargo weight
    zfw : int
        Zero Fuel Weight
    tow : int
        Take off Weight
    ldw : int
        Landing Weight
    block_fuel : int
        Block fuel
    air_distance : int
        Total air distance
    captain : str
        Captain for the flight
    dispatcher : str
        Dispatcher for the flight
    release : int
        Release number of the flightplan
    is_etops : bool
        If the flightplan is etops or not
    """
    # Identification
    icao_airline: str
    flight_number: str
    aircraft: tuple

    # Airports
    origin: str
    destination: str
    alternate: str
    # Times
    departure_time: int
    arrival_time: int
    block_time: int

    # Route
    route: str
    alt_route: str
    alt_distance:str
    initial_alt: int

    # Performance
    cruise_mach: float
    cost_index: int
    stepclimbs: str

    # Winds
    wind_dir: int
    wind_speed: int

    # Weather
    origin_metar: str
    origin_cat: str

    destination_metar: str
    destination_cat: str

    alternate_metar:str
    alternate_cat:str

    # Weights
    passengers: int
    cargo: int
    zfw: int
    tow: int
    ldw: int

    # Fuel
    block_fuel: int

    # Distance
    air_distance: int

    # Crew
    captain: str
    dispatcher: str

    # Misc
    release: str
    is_etops: bool

    # Parameters with default values
    to_alternate:str=None
    rte_alternate:str=None


    def sanitize_times(self, time):
        zulu_time = datetime.fromtimestamp(time, tz=timezone.utc).strftime("%H:%MZ")
        return zulu_time

    def alt_to_fl(self, altitude):
        ...

    def __str__(self) -> str:
        etops = "ETOPS" if self.is_etops else "NON-ETOPS"

        return (
            f"{self.icao_airline}{self.flight_number} | {self.aircraft}\n"
            f"{self.origin} → {self.destination} (ALT {self.alternate})\n"
            f"DEP {self.departure_time}  ARR {self.arrival_time}  ETE {self.block_time}\n"
            f"CRZ FL{self.initial_alt}  M{self.cruise_mach:.2f}  CI {self.cost_index}  {etops}\n"
            f"PAX {self.passengers}  CARGO {self.cargo} kg\n"
            f"ZFW {self.zfw}  TOW {self.tow}  LDW {self.ldw}\n"
            f"FUEL {self.block_fuel} kg  DIST {self.air_distance} nm\n"
            f"ROUTE: {self.route}\n"
            f"ALT RTE: {self.alt_route}\n"
            f"CAPT {self.captain} | DSP {self.dispatcher} | REL {self.release}"
        )   


async def fetch_flightplan(simbrief_id:str):


    params = {
        "username":simbrief_id,
        "json": 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(SIMBRIEF_URL, params=params) as response:
            if response.status != 200:
                return None
            data:dict = await response.json()


    
    flightplan = FlightPlan(icao_airline=data["general"]["icao_airline"],
                            flight_number=data["general"]["flight_number"],
                            aircraft=(data["aircraft"]["name"], data["aircraft"]["reg"]),
                            origin=data["origin"]["icao_code"],
                            destination=data["destination"]["icao_code"],
                            alternate=data["alternate"]["icao_code"],
                            departure_time=int(data["times"]["sched_off"]),
                            arrival_time=int(data["times"]["sched_on"]),
                            block_time=int(data["times"]["sched_block"]),
                            route=data["general"]["route"],
                            alt_route=data["alternate"]["route"],
                            initial_alt=data["general"]["initial_altitude"],
                            cruise_mach=data["general"]["cruise_mach"],
                            cost_index=data["general"]["costindex"],
                            stepclimbs=data["general"]["stepclimb_string"],
                            wind_dir=data["general"]["avg_wind_dir"],
                            wind_speed=data["general"]["avg_wind_spd"],
                            passengers=data["general"]["passengers"],
                            cargo=data["weights"]["cargo"],
                            zfw=data["weights"]["est_zfw"],
                            tow=data["weights"]["est_tow"],
                            ldw=data["weights"]["est_ldw"],
                            block_fuel=data["fuel"]["plan_ramp"],
                            air_distance=data["general"]["air_distance"],
                            captain=data["crew"]["cpt"],
                            dispatcher=data["crew"]["dx"],
                            release=data["general"]["release"],
                            is_etops=data["general"]["is_etops"],
                            origin_metar=data["origin"]["metar"],
                            origin_cat=data["origin"]["metar_category"],
                            destination_metar=data["origin"]["metar"],
                            destination_cat=data["origin"]["metar_category"],
                            to_alternate=data.get("takeoff_altn", None).get("icao_code"),
                            rte_alternate=data.get("enroute_altn", None).get("icao_code"),
                            alt_distance=data["alternate"]["distance"],
                            alternate_metar=data["alternate"]["metar"],
                            alternate_cat=data["alternate"]["metar_category"])
    
    return flightplan



def random_flight(country:str, international:bool = False, departing_airport:str = None, arrival_airport:str = None, min_distance = None, max_distance = None):
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

    sql = "SELECT name, latitude_deg, longitude_deg, ident FROM airports WHERE iso_country = ? AND type != 'heliport' AND type != 'closed'"
    cursor.execute(sql, (country,))
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

        departing_airport = (departing_airport[0][3], departing_airport[0][1])

    if arrival_airport is not None:
        arrival_airport = airport_lookup(arrival_airport)
        arrival_locked = True
        arrival_cords = (arrival_airport[0][4], arrival_airport[0][5])
        if arrival_airport == False:
            cursor.close()
            airport_db.close()
            return 3

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