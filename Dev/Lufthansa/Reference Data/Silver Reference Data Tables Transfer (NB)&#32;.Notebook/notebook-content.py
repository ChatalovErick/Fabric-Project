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

# # (1) Used to delete the Silver schema tables

# CELL ********************

# MAGIC %%sql 
# MAGIC DROP TABLE IF EXISTS Silver.lufthansadata_aircrafts;
# MAGIC DROP TABLE IF EXISTS Silver.lufthansadata_airlines;
# MAGIC DROP TABLE IF EXISTS Silver.lufthansadata_airports;
# MAGIC DROP TABLE IF EXISTS Silver.lufthansadata_cities;
# MAGIC DROP TABLE IF EXISTS Silver.lufthansadata_countries

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (1) Transfer Delta Tables from dbo to Silver schema. 

# CELL ********************

# 1. Configuration
source_schema = "dbo"
target_schema = "Silver"

# REMOVE the "Silver " prefix from these strings
tables_to_transfer = [
    "Silver_lufthansadata_aircrafts", 
    "Silver_lufthansadata_airlines", 
    "Silver_lufthansadata_airports", 
    "Silver_lufthansadata_cities", 
    "Silver_lufthansadata_countries"
]

# 2. Ensure target schema exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")

# 3. Execution loop
for table_name in tables_to_transfer:
    try:

        # This will now correctly resolve to dbo.lufthansadata_aircrafts
        df = spark.read.table(f"{source_schema}.{table_name}")

        # This will save it to Silver.lufthansadata_aircrafts
        table_name = table_name.replace("Silver_", "")
        print(f"Transferring {source_schema}.{table_name} -> {target_schema}.{table_name}")
        df.write.format("delta").mode("overwrite").saveAsTable(f"{target_schema}.{table_name}")
        
        print(f"Success!")
    except Exception as e:
        print(f"Error: {e}")

# Force-stop the session to free up capacity immediately
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
