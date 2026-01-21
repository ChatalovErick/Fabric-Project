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

from pyspark.sql.functions import current_timestamp, input_file_name
from notebookutils import mssparkutils
from datetime import datetime
from pyspark.sql.functions import explode, col

# --- Load the json data into delta tables  ---
# Create the top-level Database (Catalog level)
spark.sql("CREATE DATABASE IF NOT EXISTS Bronze")

# --- get date --- #
now = datetime.now().strftime("%Y-%m-%d")

# ---------------------------------------------- #
# Read ALL JSON files in the folder at once

raw_folder_path = f"Files/Bronze/Lufthansa Data/Operations Data/Schedule Data/{now}_germany_flight_schedules.json"

df_combined = (
            spark.read
                .option("multiline", "true")
                .json(raw_folder_path)
                .withColumn("_ingest_ts", current_timestamp())
                .withColumn("_source_file", input_file_name())
        )

# 1. Explode the array into individual rows
# This creates a new temporary column 's' for each flight object
df_exploded = df_combined.withColumn("s", explode(col("schedules")))

# 2. Select the top-level columns AND "pull out" the nested fields
df_final = df_exploded.select(
    "timestamp",              # Keep the API fetch timestamp
    "_ingest_ts",             # Keep your Fabric metadata
    "_source_file",           # Keep your Fabric metadata
    col("s.Flight_Number").alias("Flight_Number"),
    col("s.Aircraft").alias("Aircraft"),
    col("s.Origin").alias("Origin"),
    col("s.Destination").alias("Destination"),
    col("s.Departure_Time").alias("Departure_Time"),
    col("s.Arrival_Time").alias("Arrival_Time"),
    col("s.Duration").alias("Duration"),
    col("s.Has_Wifi").alias("Has_Wifi")
)

# 2. Append to a Bronze Delta Table
target_table = "Bronze.Lufthansadata_Germany_Schedule"

(df_final.write
    .format("delta")
    .mode("append") 
    .option("mergeSchema", "true") # Highly recommended if files vary slightly
    .saveAsTable(target_table))

print("✅ All Germany Status files combined and appended to the Delta Table.")

# ---------------------------------------------- #


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
