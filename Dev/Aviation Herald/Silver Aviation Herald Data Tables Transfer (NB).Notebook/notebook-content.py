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

# # (1) Transfer Delta Tables from dbo to Silver schema. 

# CELL ********************

import time
from notebookutils import mssparkutils

# 1. Configuration
source_schema = "dbo"
target_schema = "Silver"

# List of tables to transfer
tables_to_transfer = [
    "Silver_aviationheralddata",
    # Add more table names here as needed
]

# 2. Ensure target schema exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")

# 3. Execution loop (Sequential Foreach)
for original_table_name in tables_to_transfer:
    try:
        # Small sleep to allow capacity to settle between table transfers
        print(f"Starting transfer for {original_table_name}...")
        time.sleep(5) 

        # Read from source
        df = spark.read.table(f"{source_schema}.{original_table_name}")

        # Clean the table name (Remove "Silver_" prefix)
        clean_table_name = original_table_name.replace("Silver_", "")
        
        print(f"Transferring: {source_schema}.{original_table_name} -> {target_schema}.{clean_table_name}")
        
        # Write to target
        df.write.format("delta").mode("overwrite").saveAsTable(f"{target_schema}.{clean_table_name}")
        
        print(f"Successfully transferred {clean_table_name}!")
        
        # Unpersist dataframe to free up Spark memory immediately
        df.unpersist()

    except Exception as e:
        print(f"Failed to transfer {original_table_name}: {e}")

mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
