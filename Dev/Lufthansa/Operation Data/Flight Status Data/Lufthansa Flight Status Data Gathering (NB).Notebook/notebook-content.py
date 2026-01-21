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

# # (1) Used to get Operation data from the flights status happening at certain airports

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

    print(schedules)
    
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


def get_flight_status_departures_data(token, FLIGHT_STATUS_URL, limit=10):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_flight_status = []

    while True:

        time.sleep(1)
        
        try:
            params = {'lang': 'EN', 'limit': limit, 'offset': offset}
                  
            response = requests.get(FLIGHT_STATUS_URL, headers=headers, params=params)
            flight_status_data = response.json()

            # Check if Schedule exists to avoid key errors
            status = flight_status_data.get('FlightStatusResource', {}).get('Flights', []).get('Flight', [])

            TotalCount = flight_status_data['FlightStatusResource']['Meta']['TotalCount']
            
            for item in status:
        
                departure = item.get('Departure', {})
                arrival = item.get('Arrival', {})
                
                # Create a single flat row
                row = {
                    # Flight Identity
                    "Carrier": item.get('MarketingCarrier', {}).get('AirlineID'),
                    "Flight_Number": item.get('MarketingCarrier', {}).get('FlightNumber'),
                    "Aircraft_Reg": item.get('Equipment', {}).get('AircraftRegistration'),
                    "Aircraft_Code": item.get('Equipment', {}).get('AircraftCode'),
                    "type": "Departure",
                    # Departure Info
                    "Origin": departure.get('AirportCode'),
                    "Dep_Terminal": departure.get('Terminal', {}).get('Name'),
                    "Dep_Gate": departure.get('Terminal', {}).get('Gate'),
                    "Dep_Scheduled": departure.get('ScheduledTimeLocal', {}).get('DateTime'),
                    "Dep_Actual": departure.get('ActualTimeLocal', {}).get('DateTime'),
                    "Dep_Status": departure.get('TimeStatus', {}).get('Definition'),
                    
                    # Arrival Info
                    "Destination": arrival.get('AirportCode'),
                    "Arr_Terminal": arrival.get('Terminal', {}).get('Name'),
                    "Arr_Scheduled": arrival.get('ScheduledTimeLocal', {}).get('DateTime'),
                    "Arr_Estimated": arrival.get('EstimatedTimeLocal', {}).get('DateTime'),
                    "Arr_Actual": arrival.get('ActualTimeLocal', {}).get('DateTime'),
                    "Arr_Status": arrival.get('TimeStatus', {}).get('Definition'),
                    
                    # Overall Status
                    "Flight_Status": item.get('FlightStatus', {}).get('Definition'),
                    "Service_Type": item.get('ServiceType')
                }
        
                simplified_flight_status.append(row)

                offset += 1 
                
            if TotalCount <= offset:
                
                return(simplified_flight_status)
                    
                break

        except:

            print(response.status_code)
            token = get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }


def get_flight_status_arrivals_data(token, FLIGHT_STATUS_URL, limit=100):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_flight_status = []

    while True:

        time.sleep(1)

        try:
            params = {'lang': 'EN', 'limit': limit, 'offset': offset}
                  
            response = requests.get(FLIGHT_STATUS_URL, headers=headers, params=params)
            flight_status_data = response.json()

            # Check if Schedule exists to avoid key errors
            status = flight_status_data.get('FlightStatusResource', {}).get('Flights', []).get('Flight', [])

            TotalCount = flight_status_data['FlightStatusResource']['Meta']['TotalCount']
            
            for item in status:
        
                departure = item.get('Departure', {})
                arrival = item.get('Arrival', {})
                
                # Create a single flat row
                row = {
                    # Flight Identity
                    "Carrier": item.get('MarketingCarrier', {}).get('AirlineID'),
                    "Flight_Number": item.get('MarketingCarrier', {}).get('FlightNumber'),
                    "Aircraft_Reg": item.get('Equipment', {}).get('AircraftRegistration'),
                    "Aircraft_Code": item.get('Equipment', {}).get('AircraftCode'),
                    "type": "Arrival",
                    # Departure Info
                    "Origin": departure.get('AirportCode'),
                    "Dep_Terminal": departure.get('Terminal', {}).get('Name'),
                    "Dep_Gate": departure.get('Terminal', {}).get('Gate'),
                    "Dep_Scheduled": departure.get('ScheduledTimeLocal', {}).get('DateTime'),
                    "Dep_Actual": departure.get('ActualTimeLocal', {}).get('DateTime'),
                    "Dep_Status": departure.get('TimeStatus', {}).get('Definition'),
                    
                    # Arrival Info
                    "Destination": arrival.get('AirportCode'),
                    "Arr_Terminal": arrival.get('Terminal', {}).get('Name'),
                    "Arr_Scheduled": arrival.get('ScheduledTimeLocal', {}).get('DateTime'),
                    "Arr_Estimated": arrival.get('EstimatedTimeLocal', {}).get('DateTime'),
                    "Arr_Actual": arrival.get('ActualTimeLocal', {}).get('DateTime'),
                    "Arr_Status": arrival.get('TimeStatus', {}).get('Definition'),
                    
                    # Overall Status
                    "Flight_Status": item.get('FlightStatus', {}).get('Definition'),
                    "Service_Type": item.get('ServiceType')
                }
        
                simplified_flight_status.append(row)

                offset += 1 
                
            if TotalCount <= offset:
                
                return(simplified_flight_status)
                    
                break

        except:

            print(response.status_code)
            token = get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2)  Used to filter and save the germany airports connections into files


# CELL ********************

# ---------------------------------------------------- #
# Used to query aiports in all of germany

def get_germany_data():
    # get the airports in germany
    query = """
    SELECT DISTINCT(AirportCode) FROM Silver.lufthansadata_airports
    WHERE CountryCode = 'DE' and AirportCode <> '' 
    """

    Germany_official_airports = spark.sql(query)

    # 2. Transform to a Pandas DataFrame
    germany_pandas_df = Germany_official_airports.toPandas()

    # 3. Transform a specific column to a list
    airports_list = germany_pandas_df['AirportCode'].tolist()

    # Print results
    return airports_list

# ---------------------------------------------------- #

# ---------------------------------------------------- #
# Save data to a json file 

def save_aiports_connection(Aiports_connections):

    # 1. Define Paths
    relative_folder_path = "Files/Bronze/Lufthansa Data/Operations Data/Flight Status Data"
    file_name = "germany_connections.json"
    absolute_file_path = f"/lakehouse/default/{relative_folder_path}/{file_name}"

    # 2. Check if folder exists
    if mssparkutils.fs.exists(relative_folder_path):
        print(f"Folder '{relative_folder_path}' already exists.")
        
        existing_data = []

        # 3. Load existing data if the file exists
        if os.path.exists(absolute_file_path):
            try:
                with open(absolute_file_path, 'r') as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"File exists but couldn't be read: {e}")

        # 4. Filter for new data (Exact Match)
        new_items = [item for item in Aiports_connections if item not in existing_data]

        if len(new_items) > 0:
            print(f"Found {len(new_items)} new connections.")
            
            # Combine old data with only the truly new items
            final_data = existing_data + new_items

            # 5. Save back to JSON
            try:
                with open(absolute_file_path, 'w') as f:
                    json.dump(final_data, f, indent=4)
                print("File updated successfully.")
            except Exception as e:
                print(f"Error saving: {e}")
        else:
            print("No new data to add.") 
        
    else:
        print(f"Folder '{relative_folder_path}' not found. Creating it now...")
        mssparkutils.fs.mkdirs(relative_folder_path)

        # 3. Save the list of dicts
        try:
            with open(absolute_file_path, 'w') as f:
                json.dump(Aiports_connections, f, indent=4)
            print(f"Successfully saved to: {absolute_file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

# ------------------------------------ #


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

# Define your Lakehouse directory
LAKEHOUSE_PATH = "Files/Bronze/Lufthansa Data"

token = get_access_token()


FLIGHT_STATUS_URL = f"https://api.lufthansa.com/v1/operations/flightstatus/arrivals/FRA/2026-01-15T06:29"
arrivals = get_flight_status_arrivals_data(token,FLIGHT_STATUS_URL,limit=100)
print(arrivals)


FLIGHT_STATUS_URL = f"https://api.lufthansa.com/v1/operations/flightstatus/departures/FRA/2026-01-15T06:29"
departures = get_flight_status_departures_data(token,FLIGHT_STATUS_URL,limit=100)
print(departures)

'''
FLIGHT_SCHEDULES_URL = f"https://api.lufthansa.com/v1/operations/schedules/FRA/MUC/2026-01-15"
flight_data = get_flight_schedules_data(token,FLIGHT_SCHEDULES_URL,limit=100)
print(flight_data) 
'''
"""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2) Execution Code
# 
#     (1.) Firstly the code get all the airports in Germany.
#     (2.) Get the status of the flights of the FRA and MUC airports
#     
#     () Save the connections that happen between this The FRA and MUC airports with the other airports in Germany and update the json file from germany airports connections (germany_connections.json).
#     
#     Its intended to be executed in interval of 4 hours, at this moment only used to get the departures from a certain airport. The code is used to get the arrivals and departures of a specific airport, in 4 hours interval.
# 
# ## (2.1) Main-Hubs
#     
#     These two airports handle the overwhelming majority of Lufthansa's passenger and cargo volume.
# 
#     (1) FRA (Frankfurt Airport): Lufthansa’s primary hub and the busiest airport in Germany. It serves as the main gateway for long-haul flights to the Americas and Asia.
#     (2) MUC (Munich Airport): The secondary hub. It is often rated as one of the best airports in the world and handles significant transatlantic and European feeder traffic.
# 
# ## (2.2) Top German Airports (2025 Projections)
# 
#     Frankfurt (FRA):	Global Hub/Cargo;	Essential for international/intercontinental data.
#     Munich (MUC):	Premium Hub	Essential; for South Germany and business connectivity.
#     Berlin (BER):	Capital/LCC Hub;	Essential for political travel and budget airline trends.
#     Düsseldorf (DUS):	Regional/Industrial;	Captures the population-dense North Rhine-Westphalia.


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

# "FRA","MUC","BER"
Germany_Main_Hubs = ["FRA","MUC","BER"]

# Get current local time
now = datetime.now()

# 2. Subtract 4 hours
arr_time = now - timedelta(hours=4)
dep_time = now - timedelta(hours=4)

# 3. Format the adjusted time as a string
dep_formatted_time = now.strftime("%Y-%m-%dT%H:%M")
arr_formatted_time = arr_time.strftime("%Y-%m-%dT%H:%M")

Aiports_connections = []

# ---------------------------------------------------- #

def save_flight_status(airport,type,flight_status_data):

    # 1. Define Paths
    relative_folder_path = "Files/Bronze/Lufthansa Data/Operations Data/Flight Status Data"
    file_name = f"{airport}_{type}_flight_status.json"
    absolute_file_path = f"/lakehouse/default/{relative_folder_path}/{file_name}"

    # 2. Check if folder exists, if not create it
    if not mssparkutils.fs.exists(relative_folder_path):
        print(f"Directory {relative_folder_path} does not exist. Creating it...")
        mssparkutils.fs.mkdirs(relative_folder_path)
    else:
        print("Folder exists, proceeding with save.")
        pass

    # 3. Save the list of dicts from status data
    try:
        with open(absolute_file_path, 'w') as f:
            json.dump(flight_status_data, f, indent=4)
        print(f"Successfully saved to: {absolute_file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


# ---------------------------------------------------- #
# Get the Aiports that have connections in Germany

airports_list = get_germany_data()

for airport in Germany_Main_Hubs:

    # Departure
    DEP_FLIGHT_STATUS_URL = f"https://api.lufthansa.com/v1/operations/flightstatus/departures/{airport}/{dep_formatted_time}"

    try: 
        dep_flight_status_data = get_flight_status_departures_data(token,DEP_FLIGHT_STATUS_URL,limit=100)
        save_flight_status(airport,"departure",dep_flight_status_data)
    except Exception as err:
        print(f"Unable to get data from the request: {err}")
        break

    dep_df = pd.DataFrame(dep_flight_status_data)
    dep_unique_dest_list = dep_df["Destination"].unique().tolist()

    # all the departures comming from germany airports
    germany_departure_connections = list(set(airports_list) & set(dep_unique_dest_list))

    # Create {"hub", "arrival"} objects for the departures data
    for dest in germany_departure_connections:
        Aiports_connections.append({"departure": airport, "arrival": dest})

    # Arrival 
    ARR_FLIGHT_STATUS_URL = f"https://api.lufthansa.com/v1/operations/flightstatus/arrivals/{airport}/{arr_formatted_time}"

    try: 
        arr_flight_status_data = get_flight_status_arrivals_data(token,ARR_FLIGHT_STATUS_URL,limit=100)
        save_flight_status(airport,"arrival",arr_flight_status_data)
    except Exception as err:
        print(f"Unable to get data from the request: {err}")
        break

    arr_df = pd.DataFrame(arr_flight_status_data)

    arr_unique_dest_list = arr_df["Origin"].unique().tolist()

    # all the arrivals going to germany airpors
    germany_arrivals_connections = list(set(airports_list) & set(arr_unique_dest_list))

    # Create {"departure", "hub"} objects from the arrivals data
    for origin in germany_arrivals_connections:
        Aiports_connections.append({"departure": origin, "arrival": airport})

    save_aiports_connection(Aiports_connections)
    
    time.sleep(5)

# ---------------------------------------------------- #

# Force-stop the session to free up capacity immediately
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
