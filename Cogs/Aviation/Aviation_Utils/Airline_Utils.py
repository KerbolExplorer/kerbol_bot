import sqlite3
import os


AIRCRAFT_DB = os.path.join(os.path.dirname(__file__), '..', "Aviation_Databases", "aircraft.db")

def get_aircraft(airline:int, aircraft:str=None):
    db = sqlite3.connect(AIRCRAFT_DB)
    cursor = db.cursor()

    if aircraft is None:
        sql = "SELECT * FROM AircraftList WHERE airlineId = ?"
        cursor.execute(sql, (airline,))
        aircraft = cursor.fetchall()
    else:
        sql = "SELECT * FROM AircraftList WHERE airlineId = ? AND registration = ?"
        cursor.execute(sql, (airline, aircraft))
        aircraft = cursor.fetchone()

    if aircraft == None:
        db.close()
        return []
    else:
        db.close()
        return aircraft
    