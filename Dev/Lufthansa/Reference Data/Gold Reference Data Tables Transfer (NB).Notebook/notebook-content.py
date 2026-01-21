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

# # (1) Transfer Delta Tables from dbo to Gold schema. 

# CELL ********************

# 1. Configuration
source_schema = "dbo"
target_schema = "Gold"

# REMOVE the "Silver " prefix from these strings
tables_to_transfer = [
    "Gold_lufthansadata_aircrafts", 
    "Gold_lufthansadata_airlines", 
    "Gold_lufthansadata_airports"
]

# 2. Ensure target schema exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")

# 3. Execution loop
for table_name in tables_to_transfer:
    try:

        # This will now correctly resolve to dbo.lufthansadata_aircrafts
        df = spark.read.table(f"{source_schema}.{table_name}")

        # This will save it to Silver.lufthansadata_aircrafts
        table_name = table_name.replace("Gold_", "")
        print(f"Transferring {source_schema}.{table_name} -> {target_schema}.{table_name}")
        df.write.format("delta").mode("overwrite").saveAsTable(f"{target_schema}.{table_name}")
        
        print(f"Success!")
    except Exception as e:
        print(f"Error: {e}")

# Replace with your actual table name
table_name = "Gold.lufthansadata_airports"

spark.sql(f"""
    INSERT INTO {table_name} 
    VALUES ('FRA', 'Frankfurt', 'FRA', 'DE', 'Frankfurt', 'Germany'),
    ('BER', 'Berlin Brandenburg Airport', 'BER', 'DE', 'Berlin', 'Germany')
""")

# Force-stop the session to free up capacity immediately
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
