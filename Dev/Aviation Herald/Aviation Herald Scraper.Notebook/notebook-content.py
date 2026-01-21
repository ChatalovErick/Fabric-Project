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

# # (1) Get multiple days worth of data (full load)

# CELL ********************

import requests
from bs4 import BeautifulSoup
import json
import re
import random
from datetime import datetime, timedelta
import time
import os

# --- 2. CONFIGURATION & HELPERS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

def format_date(date_string):
    try:
        clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_string)
        parts = clean_date.split() 
        if len(parts) >= 4:
            date_part = f"{parts[1]} {parts[2]} {parts[3]}"
            dt = datetime.strptime(date_part, "%b %d %Y")
            return dt
        return None
    except: return None

# --- 3. SCRAPING ENGINE ---
def Scrape_Aviation_Herald_Full_Load(days_to_collect=90):
    aggregated_data = {}
    target_date = datetime.now() - timedelta(days=days_to_collect)
    
    session = requests.Session()
    current_url = "https://avherald.com/?listby=date"
    reached_target = False

    while not reached_target:
        print(f"Fetching: {current_url}")
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": "https://avherald.com/"
        }

        try:
            # Human-like delay
            time.sleep(random.uniform(10, 15))
            response = session.get(current_url, headers=headers, timeout=15)
            response.raise_for_status()

        except Exception as e:
            print(f"Error: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all('span', class_=['bheadline_avherald', 'headline_avherald'])
        
        if not elements:
            print(f"No headlines found. Length of HTML: {len(response.text)}")
            # Useful to see if you got a 'blocked' page
            if "blocked" in response.text.lower():
                print("Warning: It looks like AvHerald has blocked this request.")
            break

        current_date_iso = None
        last_processed_dt = None

        for span in elements:
            classes = span.get('class', [])
            text = span.get_text(strip=True)

            if 'bheadline_avherald' in classes:
                dt_object = format_date(text)
                if dt_object:
                    if dt_object < target_date:
                        reached_target = True
                        break
                    last_processed_dt = dt_object
                    current_date_iso = dt_object.strftime("%Y-%m-%d")
                    aggregated_data.setdefault(current_date_iso, [])
            
            elif 'headline_avherald' in classes and current_date_iso:
                img_tag = span.find_previous('img', class_='frame')
                event_type = img_tag.get('alt', 'Unknown') if img_tag else 'Unknown'
                aggregated_data[current_date_iso].append({
                    "type": event_type, "headline": text
                })

        if reached_target or not last_processed_dt: break
        current_url = f"https://avherald.com/?listby=date&offset={last_processed_dt.strftime('%Y%m%d')}"

    return aggregated_data

def Save_To_Lakehouse_Full_Load(data, base_path="/lakehouse/default/Files/Bronze/Aviation Herald Data"):
    """
    Groups data by Year and Month and saves them into a specific JSON structure:
    {'timestamp': 'YYYY-MM-DD', 'items': [...]}
    """
    # 1. Group the original data by YYYY-MM
    partitions = {}
    
    for date_str, events in data.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year_month = dt.strftime("%Y-%m")
        
        if year_month not in partitions:
            partitions[year_month] = []
        
        # 2. TRANSFORM HERE: Create the specific dictionary structure you requested
        transformed_entry = {
            "timestamp": date_str,
            "items": events
        }
        partitions[year_month].append(transformed_entry)

    # 3. Save each month to its specific directory
    for year_month, monthly_list in partitions.items():
        year, month = year_month.split("-")
        
        folder_path = os.path.join(base_path, f"Year={year}", f"Month={month}")
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, "data.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            # We save the list of daily objects
            json.dump(monthly_list, f, indent=4)
            
    print(f"Successfully saved structured data to {base_path}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2) Get only one day worth of data (incremental load)

# CELL ********************

import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_ordinal_suffix(day):
    """Returns the suffix (st, nd, rd, th) for a day of the month."""
    if 11 <= day <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

def format_for_avherald(iso_date_str):
    """Converts '2026-01-12' to 'Monday Jan 12th 2026'"""
    dt = datetime.strptime(iso_date_str, "%Y-%m-%d")
    day_name = dt.strftime("%A")
    month_name = dt.strftime("%b")
    day_num = dt.day
    suffix = get_ordinal_suffix(day_num)
    year = dt.year
    return f"{day_name} {month_name} {day_num}{suffix} {year}"

def Scrape_Aviation_Herald_Incremental_Load(iso_target_date):
    # 1. Convert the chosen date (YYYY-MM-DD) to the website's header format
    target_header = format_for_avherald(iso_target_date)
    print(f"Searching for header: {target_header}")

    url = "https://avherald.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}

    time.sleep(2) # Reduced delay for efficiency
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Find the specific date header
    date_span = soup.find('span', class_='bheadline_avherald', string=target_header)
    
    if not date_span:
        print(f"No entries found for {target_header} on the front page.")
        return None

    events = []

    # 3. Scrape events following the date span
    for element in date_span.find_all_next():
        # Stop if we hit the next day's header
        if element.name == 'span' and 'bheadline_avherald' in element.get('class', []):
            break
        
        # Capture headlines
        if element.name == 'span' and 'headline_avherald' in element.get('class', []):
            parent_table = element.find_parent('table')
            img_tag = parent_table.find('img', class_='frame') if parent_table else None
            
            events.append({
                "headline": element.get_text(strip=True),
                "type": img_tag.get('alt') if img_tag else "Unknown"
            })

    return {
        "timestamp": iso_target_date,
        "items": events
    }


def Save_To_Lakehouse_Incremental_Load(data, base_path="/lakehouse/default/Files/Bronze/Aviation Herald Data"):
    # 1. Get current time for partitioning
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')

    # 2. SEPARATE folder from file
    # folder_path is for creating the directory
    # file_path is for saving the actual JSON
    folder_path = os.path.join(base_path, f"Year={year}", f"Month={month}")
    file_path = os.path.join(folder_path, "data.json")

    # 3. Create the directory (not the file)
    os.makedirs(folder_path, exist_ok=True)

    try:
        dataset = []
        # 4. Read existing data if it exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as f:
                try:
                    dataset = json.load(f)
                    if not isinstance(dataset, list):
                        dataset = [dataset]
                except json.JSONDecodeError:
                    dataset = []

        # 5. Prevent Duplicates: Remove entry if this day was already scraped
        dataset = [entry for entry in dataset if entry.get("timestamp") != data.get("timestamp")]
        dataset.append(data)

        # 6. Save back to OneLake
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(dataset, f, indent=4)
        
        print(f"Successfully updated: {file_path}")

    except Exception as e:
        print(f"Failed to update: {str(e)}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (3) Code Execution

# CELL ********************

# 1. Define your base path as a variable to ensure consistency
# For notebookutils:
relative_base_path = "Files/Bronze/Aviation Herald Data"
# For 'os' and 'open' functions:
posix_base_path = "/lakehouse/default/Files/Bronze/Aviation Herald Data"

# Check if the root folder exists
if notebookutils.fs.exists(relative_base_path):
    print(f"✅ Folder '{relative_base_path}' exists.")

    # Use today's date for incremental load
    today = datetime.now()
    chosen_day = today.strftime("%Y-%m-%d")

    scraped_result = Scrape_Aviation_Herald_Incremental_Load(chosen_day)

    if scraped_result and scraped_result.get("items"):
        # Pass the POSIX path to your saving function
        Save_To_Lakehouse_Incremental_Load(scraped_result, base_path=posix_base_path)
    else:
        print(f"ℹ️ No new headlines found for {chosen_day}. Skipping save.")

else:
    print(f"❌ Folder '{relative_base_path}' not found. Starting Full Load...")

    # Create the folder
    notebookutils.fs.mkdirs(relative_base_path)
    print(f"✅ Folder '{relative_base_path}' created.")

    # Run Full Load (e.g., last 365 days)
    data = Scrape_Aviation_Herald_Full_Load(days_to_collect=365)
    
    if data:
        Save_To_Lakehouse_Full_Load(data, base_path=posix_base_path)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
