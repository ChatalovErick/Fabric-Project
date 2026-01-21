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

# # (1) Code To Create the Delta tables from lufthansa data

# CELL ********************

from pyspark.sql.functions import current_timestamp, input_file_name
from notebookutils import mssparkutils

def ingest_json_to_bronze(file_name, table_name):

    # 1. FIX THE PATH: Use the Fabric local mount point
    # This resolves the abfss error you are seeing
    base_path = "Files/Bronze/Lufthansa Data/"
    full_path = f"{base_path}{file_name}"
    
    # Target table name using your requested format
    target_table = f"Bronze.LufthansaData_{table_name}"

    print(f"Starting ingestion for: {full_path} into table: {target_table}")
    
    try:
        # 3. Read the data
        df = (
            spark.read
                .option("multiline", "true")
                .json(full_path)
                .withColumn("_ingest_ts", current_timestamp())
                .withColumn("_source_file", input_file_name())
        )
        
        # 4. Write/Rewrite the data
        # 'overwrite' deletes and replaces the data
        # 'overwriteSchema' allows the structure to change (like your Airports list fix)
        (df.write
          .format("delta")
          .mode("overwrite")
          .option("overwriteSchema", "true") 
          .saveAsTable(target_table))
          
        print(f"✅ Successfully REWRITTEN {file_name} into {target_table}.")
        
    except Exception as e:
        # Check if the file actually exists if it still fails
        if "PATH_NOT_FOUND" in str(e):
            print(f"❌ File not found at: {full_path}")
            print("Please check if the 'Lufthansa Data' folder exists in the Files section.")
        else:
            print(f"❌ Error loading {file_name}: {e}")

# --- Load the json data into delta tables  ---

# Create the top-level Database (Catalog level)
spark.sql("CREATE DATABASE IF NOT EXISTS Bronze")

# Save data to a table
ingest_json_to_bronze("countries.json", "Countries")
ingest_json_to_bronze("cities.json", "Cities")
ingest_json_to_bronze("airports.json", "Airports")
ingest_json_to_bronze("airlines.json", "Airlines")
ingest_json_to_bronze("aircrafts.json", "Aircrafts")

# Force-stop the session to free up capacity immediately
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2) Display data if necessary

# CELL ********************

# View the table you just created

#df = spark.read.table("countries")
#display(df)

#df = spark.read.table("Bronze.lufthansadata_cities")
#display(df)

#df = spark.read.table("Bronze.lufthansadata_airports")
#display(df)

#df = spark.read.table("Bronze.lufthansadata_airlines")
#display(df)

#df = spark.read.table("Bronze.lufthansadata_aircrafts")
#display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
