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

# # (1) Used to Delete the Delta tables in the dbo schema during the pipeline 

# CELL ********************

# MAGIC %%sql 
# MAGIC DROP TABLE IF EXISTS dbo.Silver_aviationheralddata;


# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Force-stop the session to free up capacity immediately
mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
