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

# # (1) Transfer flight status data from the dbo schema to the Silver schema

# CELL ********************

from delta.tables import DeltaTable

source_table = "dbo.Silver_lufthansadata_germany_flight_status"
target_table = "Silver.lufthansadata_germany_flight_status"

# 1. Read the intermediate data
df_updates = spark.read.table(source_table)

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
        target.FlightStatusId = updates.FlightStatusId AND 
        target.ScheduledArrivalTime = updates.ScheduledArrivalTime AND 
        target.ScheduledDepartureTime = updates.ScheduledDepartureTime
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


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # (2)  Transfer aiport connections data from the dbo schema to the Silver schema

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

source_table = "dbo.Silver_lufthansadata_germany_flight_status"
target_table = "Silver.lufthansadata_germany_flight_status"

# 1. Read the intermediate data
df_raw = spark.read.table(source_table)

# 3. Check and Create if missing
if not spark.catalog.tableExists(target_table):
    print(f"Creating new table: {target_table}")
    df_updates.write.format("delta").saveAsTable(target_table)
else:
    print(f"Upserting into: {target_table}")
    target_delta_table = DeltaTable.forName(spark, target_table)

    # 4. Define the composite join condition
    join_condition = """
        target.FlightStatusId = updates.FlightStatusId AND 
        target.ScheduledArrivalTime = updates.ScheduledArrivalTime AND 
        target.ScheduledDepartureTime = updates.ScheduledDepartureTime
    """

    # 5. Execute Merge
    (target_delta_table.alias("target")
      .merge(
        df_updates.alias("updates"),
        join_condition
      )
      .whenMatchedUpdateAll()
      .whenNotMatchedInsertAll()
      .execute()
    )

# Force-stop the session
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
