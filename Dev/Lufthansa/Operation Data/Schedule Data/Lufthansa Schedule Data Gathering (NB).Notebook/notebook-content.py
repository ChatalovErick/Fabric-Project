# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "03daaee2-6456-4fe2-9853-752caeb5fb49",
# META       "default_lakehouse_name": "Fabric_Project_LakeHouse",
# META       "default_lakehouse_workspace_id": "228ebd15-8b0c-487d-a9f9-d00961af4eea",
# META       "known_lakehouses": [
# META         {
# META           "id": "03daaee2-6456-4fe2-9853-752caeb5fb49"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # (1) Used to get Operation data from the schedules for certain routes in some specific airports

# CELL ********************

def get_access_token():
    
    """Retrieves the OAuth 2.0 Bearer token."""
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(TOKEN_URL, data=payload)
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get token: {response.text}")


def get_flight_schedules_data(token, FLIGHT_SCHEDULES_URL, limit=10):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_flight_schedules = []
    params = {'lang': 'EN', 'limit': limit, 'offset': offset}
            
    response = requests.get(FLIGHT_SCHEDULES_URL, headers=headers, params=params)
    flight_schedules_data = response.json()

    # Check if Schedule exists to avoid key errors
    schedules = flight_schedules_data.get('ScheduleResource', {}).get('Schedule', [])

    # If only one schedule is returned, it's a dict. We must wrap it in a list.
    if isinstance(schedules, dict):
        schedules = [schedules]

    for item in schedules:

        flight_data = item.get('Flight', {})

        # --- FIX STARTS HERE ---
        # If flight_data is a list (connecting flights), handle the segments
        if type(flight_data) == type([]):
            first_segment = flight_data[0]
            last_segment = flight_data[-1]
            # For the "Flight Number", you might want to show the first one or both
            flight_number = f"{first_segment.get('MarketingCarrier', {}).get('AirlineID')}{first_segment.get('MarketingCarrier', {}).get('FlightNumber')}"
            equipment = first_segment.get('Equipment', {})
            departure = first_segment.get('Departure', {})
            arrival = last_segment.get('Arrival', {})
            carrier = first_segment.get('MarketingCarrier', {})
        else:
            # It's a single dictionary (direct flight)
            departure = flight_data.get('Departure', {})
            arrival = flight_data.get('Arrival', {})
            carrier = flight_data.get('MarketingCarrier', {})
            equipment = flight_data.get('Equipment', {})
            flight_number = f"{carrier.get('AirlineID', '')}{carrier.get('FlightNumber', '')}"
            
        # --- FIX ENDS HERE ---
        
        # Safely extract amenities
        compartments = equipment.get('Compartment', [{}])
        first_comp = compartments[0] if type(compartments) == list else {}

        row = {
            "Flight_Number": flight_number,
            "Aircraft": equipment.get('AircraftCode'),
            "Origin": departure.get('AirportCode'),
            "Origin_Terminal": departure.get('Terminal', {}).get('Name', 'N/A'),
            "Departure_Time": departure.get('ScheduledTimeLocal', {}).get('DateTime'),
            "Destination": arrival.get('AirportCode'),
            "Destination_Terminal": arrival.get('Terminal', {}).get('Name', 'N/A'),
            "Arrival_Time": arrival.get('ScheduledTimeLocal', {}).get('DateTime'),
            "Duration": item.get('TotalJourney', {}).get('Duration'),
            "Has_Wifi": first_comp.get('FlyNet', False),
            "Has_Power": first_comp.get('SeatPower', False),
            "Stops": item.get('Details', {}).get('Stops', {}).get('StopQuantity', 0)
        }

        simplified_flight_schedules.append(row)
        
    return simplified_flight_schedules

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Code Tests

# CELL ********************


"""
import requests

CLIENT_ID = "wea4mxmnzbafvmx9pca7mwccz"
CLIENT_SECRET = "HyxCaK9hXP"

TOKEN_URL = "https://api.lufthansa.com/v1/oauth/token"

# "FRA","MUC"
Germany_Main_Hubs = ["FRA","MUC"]

token = get_access_token()

FLIGHT_SCHEDULES_URL = f"https://api.lufthansa.com/v1/operations/schedules/MUC/FRA/2026-01-22"
flight_data = get_flight_schedules_data(token,FLIGHT_SCHEDULES_URL,limit=100)
print(len(flight_data))
print(flight_data)
"""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2) Execution Code

# CELL ********************

import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta
import json
import pandas as pd
import time
import os

# ================== #
# Client credentials #
CLIENT_ID = "wea4mxmnzbafvmx9pca7mwccz"
CLIENT_SECRET = "HyxCaK9hXP"
# ======================== #
# Get token for connection #
TOKEN_URL = "https://api.lufthansa.com/v1/oauth/token"
token = get_access_token()
# ======================== #

# Get current local time
now = datetime.now().strftime("%Y-%m-%d")

df = spark.read.table("Silver.lufthansadata_germany_airport_connections").toPandas()
airport_connections = df[["arrival","departure"]]

# 1. Initialize an empty list to store all flight data
all_schedules = []

for row in airport_connections.itertuples():
    print(f"Fetching: {row.departure} to {row.arrival}")
    dep = row.departure
    arr = row.arrival

    FLIGHT_SCHEDULES_URL = f"https://api.lufthansa.com/v1/operations/schedules/{dep}/{arr}/{now}"
    
    try:
        flight_data = get_flight_schedules_data(token, FLIGHT_SCHEDULES_URL, limit=100)
        
        # 2. Append the data to your list
        # We include the route info so you know which data belongs to which city pair
        all_schedules.append({
            "departure": dep,
            "arrival":arr,
            "timestamp": datetime.now().isoformat(),
            "schedules": flight_data
        })
    except Exception as e:
        print(f"Error fetching {dep}-{arr}: {e}")

    time.sleep(1)

import os

folder_path = "/lakehouse/default/Files/Bronze/Lufthansa Data/Operations Data/Schedule Data/"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

file_path = f"/lakehouse/default/Files/Bronze/Lufthansa Data/Operations Data/Schedule Data/{now}_germany_flight_schedules.json"
with open(file_path, "w") as f:
    json.dump(all_schedules, f, indent=4)

print(f"Successfully saved {len(all_schedules)} routes to {file_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
