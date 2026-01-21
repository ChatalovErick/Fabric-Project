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

# CELL ********************

import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta
import time
import json
import os

CLIENT_ID = "wea4mxmnzbafvmx9pca7mwccz"
CLIENT_SECRET = "HyxCaK9hXP"

# Endpoints
TOKEN_URL = "https://api.lufthansa.com/v1/oauth/token"
COUNTRIES_URL = "https://api.lufthansa.com/v1/mds-references/countries"
CITIES_URL = "https://api.lufthansa.com/v1/mds-references/cities"
AIRPORTS_URL = "https://api.lufthansa.com/v1/mds-references/airports"
AIRLINES_URL = "https://api.lufthansa.com/v1/mds-references/airlines"
AIRCRAFTS_URL =  "https://api.lufthansa.com/v1/mds-references/aircraft"

# Define your Lakehouse directory
LAKEHOUSE_PATH = "Files/Bronze/Lufthansa Data"

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

def save_to_lakehouse(data, filename):
    """Helper function to save JSON data to the Lakehouse folder."""
    full_path = f"/lakehouse/default/{LAKEHOUSE_PATH}/{filename}"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved to: {full_path}")

def get_countries_info(token,COUNTRIES_URL,limit= 100):

    print("\n")
    print("Getting Lufthansa Countries data")

    """Fetches countries details using the Bearer token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    offset = 0
    simplified_countries = []
    
    while True:

        time.sleep(1)

        try:
            # Parameters can include 'lang' (e.g., 'EN')
            params = {'lang':'EN','limit':limit,'offset':offset}
            
            response = requests.get(COUNTRIES_URL, headers=headers, params=params)
            countries_data = response.json()
            
            TotalCount = countries_data['CountryResource']['Meta']['TotalCount']
        
            for item in countries_data['CountryResource']['Countries']['Country']:
                simplified_countries.append({"countryCode": item["CountryCode"],"countryName": item["Names"]["Name"]["$"]})
                offset += 1
    
            if TotalCount <= offset:
    
                save_to_lakehouse(simplified_countries, "countries.json")
    
                break 

        except Exception as e:

            print(f"Error: {e}. Refreshing token...")

            token = get_access_token()

            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

def get_cities_info(token,CITIES_URL,limit=100):

    print("\n")
    print("Getting Lufthansa Cities data")

    """Fetches Cities details using the Bearer token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_cities = []

    while True:

        time.sleep(1)
        
        try:
            # Parameters can include 'lang' (e.g., 'EN')
            params = {'lang':'EN','limit':limit,'offset':offset}
            
            response = requests.get(CITIES_URL, headers=headers, params=params)
            cities_data = response.json()
            
            TotalCount = cities_data['CityResource']['Meta']['TotalCount']
            
            for item in cities_data['CityResource']['Cities']['City']:
        
                airports = item.get('Airports', {}).get('AirportCode', [])
                
                simplified_cities.append({
                    "CityCode": item["CityCode"],
                    "CountryCode":item["CountryCode"],
                    "CityName": item["Names"]["Name"]["$"],
                    "UtcOffset": item["UtcOffset"],
                    "TimeZoneId": item["TimeZoneId"],
                    "Airports": airports
                    })
                
                offset += 1
    
            if TotalCount <= offset:
                save_to_lakehouse(simplified_cities, "cities.json")

                break 

        except Exception as e:

            print(f"Error: {e}. Refreshing token...")
        
            token = get_access_token()

            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

def get_airports_info(token,AIRPORTS_URL,limit=100):

    print("\n")
    print("Getting Lufthansa Airports data")

    """Fetches Cities details using the Bearer token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_airports = []

    while True:

        time.sleep(1)

        try:
   
            # Parameters can include 'lang' (e.g., 'EN')
            params = {'lang':'EN','limit':limit,'offset':offset,'LHoperated':1}
                
            response = requests.get(AIRPORTS_URL, headers=headers, params=params)
            airport_data = response.json()
            print(airport_data)

            TotalCount = airport_data['AirportResource']['Meta']['TotalCount']
            
            for item in airport_data['AirportResource']['Airports']['Airport']:
        
                    position = item.get("Position", {}).get("Coordinate", {})
                 
                    simplified_airports.append({
                        "AirportCode": item["AirportCode"],
                        "AirportName": item["Names"]["Name"]["$"],
                        "Coordinates":position,
                        "CityCode": item["CityCode"],
                        "CountryCode": item["CountryCode"],
                        "LocationType": item["LocationType"],
                        "UtcOffset": item["UtcOffset"],
                        "TimeZoneId": item["TimeZoneId"] 
                        })
                    
                    offset += 1
                
            if TotalCount <= offset:
                
                save_to_lakehouse(simplified_airports, "airports.json")
    
                break 
        
        except Exception as e:

            print(f"Error: {e}. Refreshing token...")
            
            token = get_access_token()

            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

def get_airlines_info(token,AIRLINES_URL,limit=100):
    
    print("\n")
    print("Getting Lufthansa Airlines data")

    """Fetches Cities details using the Bearer token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_airlines = []
    
    while True:

        time.sleep(1)

        try:
            # Parameters can include 'lang' (e.g., 'EN')
            params = {'lang':'EN','limit':limit,'offset':offset}
            
            response = requests.get(AIRLINES_URL, headers=headers, params=params)
            airlines_data = response.json()
            
            TotalCount = airlines_data['AirlineResource']['Meta']['TotalCount']
        
            for item in airlines_data['AirlineResource']['Airlines']['Airline']:
                simplified_airlines.append({
                                "AirlineID": item["AirlineID"],
                                "AirlineName": item.get("Names", {}).get("Name", {}).get("$", None),
                                "AirlineID_ICAO": item["AirlineID_ICAO"] if "AirlineID_ICAO" in item else None
                                })
                
                offset += 1      
                
            if TotalCount <= offset:
                
                save_to_lakehouse(simplified_airlines, "airlines.json")

                break
                
        except Exception as e:

            print(f"Error: {e}. Refreshing token...")
            
            token = get_access_token()

            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

def get_aircrafts_info(token,AIRCRAFTS_URL,limit=100):
    
    print("\n")
    print("Getting Lufthansa Aircrafts data")

    """Fetches Cities details using the Bearer token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    offset = 0
    simplified_aircrafts = []
    
    while True:

        time.sleep(1)
    
        try:
            # Parameters can include 'lang' (e.g., 'EN')
            params = {'lang':'EN','limit':limit,'offset':offset}
            
            response = requests.get(AIRCRAFTS_URL, headers=headers, params=params)
            aircrafts_data = response.json()
            
            TotalCount = aircrafts_data['AircraftResource']['Meta']['TotalCount']

            for item in aircrafts_data['AircraftResource']['AircraftSummaries']['AircraftSummary']:
                                        
                    simplified_aircrafts.append({
                                    "AircraftCode": item["AircraftCode"] if "AircraftCode" in item else None,
                                    "AircraftName": item.get("Names", {}).get("Name", {}).get("$", None),
                                    "AirlineEquipCode": item["AirlineEquipCode"] if "AirlineEquipCode" in item else None
                                    })
                    
                    offset += 1      
                    
            if TotalCount <= offset:

                save_to_lakehouse(simplified_aircrafts, "aircrafts.json")
                    
                break
                    
        except Exception as e:

            print(f"Error: {e}. Refreshing token...")
            
            token = get_access_token()
    
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }

# Create the folder if it doesn't exist (Fabric/Spark environments)
if not os.path.exists(f"/lakehouse/default/{LAKEHOUSE_PATH}"):
    os.makedirs(f"/lakehouse/default/{LAKEHOUSE_PATH}", exist_ok=True)

# Execution
token = get_access_token()

# Get the data from countries in lufthansa developer center
get_countries_info(token,COUNTRIES_URL,100)

# Get the data from cities in lufthansa developer center
get_cities_info(token,CITIES_URL,100)

# Get the data from the airports operated by lufthansa developer center
get_airports_info(token,AIRPORTS_URL,limit=100)

# Get the Airlines data in lufthansa developer center
get_airlines_info(token,AIRLINES_URL,limit=100)

# Get the data from the airports operated by lufthansa developer center
get_aircrafts_info(token,AIRCRAFTS_URL,limit=100)

print("\n")
print("Run Finished")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
