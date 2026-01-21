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

# # (1) Code To Create the Delta tables from Aviation Herald Data

# CELL ********************

from pyspark.sql.functions import explode, col

path = "Files/Bronze/Aviation Herald Data/"

# 1. Read the JSON
df_raw = spark.read.option("multiLine", "true").json(path)

# 2. Flatten and KEEP the partition columns
# Notice we include "Year" and "Month" in BOTH select statements
df_flattened = df_raw.select(
    col("timestamp"),
    col("Year"), 
    col("Month"),
    explode(col("items")).alias("item")
).select(
    "timestamp",
    "Year",
    "Month",
    "item.headline",
    "item.type"
)

# 3. Save to Delta
df_flattened.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("Bronze.AviationHeraldData")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
