"""Airline Utils
This script contains several functions that are useful for the airline system
Current functions are:

    * get_aircraft: Gets all aircraft belonging to the airline id given, or sends the info of the aircraft handed.

"""
import sqlite3
import os


AIRCRAFT_DB = os.path.join(os.path.dirname(__file__), '..', "Aviation_Databases", "aircraft.db")

def get_aircraft(airline:int, aircraft:str=None):
    """Gets all aircraft belonging to the airline id given, or sends the info of the aircraft handed.

    Parameters
    ----------
    airline : int
        Id of the airline we want to search.
    aircraft : aircraft
        Registration of the aircraft we want to get the info from

    Returns
    ----------
    list
        A list of list containing the information of the aircraft.
    """
    db = sqlite3.connect(AIRCRAFT_DB)
    cursor = db.cursor()

    if aircraft is None:
        sql = "SELECT * FROM AircraftList WHERE airlineId = ?"
        cursor.execute(sql, (airline,))
        aircraft = cursor.fetchall()
    else:
        sql = "SELECT * FROM AircraftList WHERE airlineId = ? AND registration = ?"
        cursor.execute(sql, (airline, aircraft))
        aircraft = cursor.fetchall()

    if aircraft == None:
        db.close()
        return []
    else:
        db.close()
        return aircraft
    