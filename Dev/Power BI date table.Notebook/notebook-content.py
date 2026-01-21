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

from pyspark.sql import functions as F
from pyspark.sql.types import DateType
import datetime

# 1. Define the date range
start_date = "2020-01-01"
end_date = "2030-12-31"

# 2. Generate a sequence of dates
df = spark.range(1).select(
    F.explode(
        F.sequence(
            F.to_date(F.lit(start_date)), 
            F.to_date(F.lit(end_date)), 
            F.expr("interval 1 day")
        )
    ).alias("Date")
)

# 3. Add calendar attributes
date_table = df.select(
    F.col("Date"),
    F.year("Date").alias("Year"),
    F.month("Date").alias("MonthNumber"),
    F.date_format("Date", "MMMM").alias("MonthName"),
    F.date_format("Date", "MMM").alias("MonthShort"),
    F.quarter("Date").alias("Quarter"),
    F.concat(F.lit("Q"), F.quarter("Date")).alias("QuarterLabel"),
    F.dayofmonth("Date").alias("DayOfMonth"),
    F.dayofweek("Date").alias("DayOfWeekNumber"),
    F.date_format("Date", "EEEE").alias("DayOfWeekName"),
    F.weekofyear("Date").alias("WeekOfYear"),
    # Create a numeric YearMonth (e.g., 202401) for easy sorting
    (F.year("Date") * 100 + F.month("Date")).alias("YearMonthKey")
)

# 4. Save as a Delta Table in your Lakehouse
date_table.write.mode("overwrite").format("delta").saveAsTable("Gold.Date_Table")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
