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

# # (1) Code To Create the Delta tables from lufthansa operations data

# CELL ********************

from notebookutils import mssparkutils
from pyspark.sql.window import Window # Add this line
from pyspark.sql.functions import current_timestamp, input_file_name, row_number
from delta.tables import DeltaTable 

def ingest_json_to_bronze(file_name, table_name):

    # 1. FIX THE PATH: Use the Fabric local mount point
    # This resolves the abfss error you are seeing
    base_path = "Files/Bronze/Lufthansa Data/Operations Data/Flight Status Data"
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
ingest_json_to_bronze("germany_connections.json", "Germany_airport_connections")

# ---------------------------------------------- #
# Read ALL JSON files in the folder at once

# 1. Read the new data
raw_folder_path = "Files/Bronze/Lufthansa Data/Operations Data/Flight Status Data/*_status.json"
df_new_raw = (spark.read
              .option("multiline", "true")
              .json(raw_folder_path)
              .withColumn("_ingest_ts", current_timestamp())
              .withColumn("_source_file", input_file_name()))

# 2. Deduplicate: This handles your requirement to "add the newest and remove the oldest"
# if multiple files for the same flight exist in the source folder.
windowSpec = Window.partitionBy("Flight_Number", "Dep_Scheduled").orderBy(current_timestamp().desc())
df_new = df_new_raw.withColumn("rn", row_number().over(windowSpec)).filter("rn = 1").drop("rn")

target_table = "Bronze.Lufthansadata_Germany_Flight_Status"

# 3. Perform the Merge (Upsert)
if spark.catalog.tableExists(target_table):
    deltaTable = DeltaTable.forName(spark, target_table)
    
    # Matching on Flight Number and Scheduled Departure
    join_condition = (
        "target.Flight_Number = updates.Flight_Number AND "
        "target.Dep_Scheduled = updates.Dep_Scheduled"
    )

    deltaTable.alias("target") \
        .merge(
            df_new.alias("updates"),
            join_condition
        ) \
        .whenMatchedUpdateAll() \
        .whenNotMatchedInsertAll() \
        .execute()
    print("Merge successful: Newest data updated, duplicates handled.")
else:
    # Initial load if table doesn't exist
    df_new.write.format("delta").mode("overwrite").saveAsTable(target_table)
    print("Table created and initial data loaded.")

# ---------------------------------------------- #


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
