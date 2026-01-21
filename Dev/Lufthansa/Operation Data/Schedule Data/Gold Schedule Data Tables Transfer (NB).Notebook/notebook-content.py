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

from delta.tables import DeltaTable

source_table = "dbo.Gold_lufthansadata_germany_schedule"
target_table = "Gold.lufthansadata_germany_schedule"

# 1. Read the intermediate data
df_updates = spark.read.table(source_table)

# 1. Read and DEDUPLICATE the source data
# We drop duplicates based on the keys you use for the Merge
df_updates = (
    spark.read.table(source_table)
    .dropDuplicates(["FlightNumber", "ArrivalTime", "DepartureTime"])
)

# 2. Check and Create if missing
if not spark.catalog.tableExists(target_table):
    print(f"Creating new table: {target_table}")
    df_updates.write.format("delta").saveAsTable(target_table)
else:
    print(f"Upserting into: {target_table}")
    target_delta_table = DeltaTable.forName(spark, target_table)

    # 3. Define the composite join condition
    # We use 'AND' to ensure all three columns match for an update to occur
    join_condition = """
        target.FlightNumber = updates.FlightNumber AND 
        target.DepartureTime = updates.DepartureTime
    """

    # 4. Execute Merge
    (target_delta_table.alias("target")
      .merge(
        df_updates.alias("updates"),
        join_condition
      )
      .whenMatchedUpdateAll()     # Updates the full row if the key matches
      .whenNotMatchedInsertAll()  # Inserts the full row if the key is new
      .execute()
    )

mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
