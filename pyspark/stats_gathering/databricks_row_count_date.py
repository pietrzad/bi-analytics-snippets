# 1) catalog.schema.monitoring_table has to be changed to your desired FQTN
# 2) tables in list below have to be changed to the ones you woild like to gather stats about

from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql import DataFrame
from pyspark.sql.window import Window

-----------------------------------------------------------------------------------------------------------------------

# adding all tables for which logs are needed
tables = [
    "catalog.schema.table",
    "catalog.schema.table"
]

-----------------------------------------------------------------------------------------------------------------------

# helper function to split full table path to separate catalog/schema/table columns before writing to final stats table
def split_path(df: DataFrame) -> DataFrame:
    parts = F.split(F.col("path"), "\\.")
    return (
        df
        .withColumn("catalog", F.when(F.size(parts) >= 1, parts[0]))
        .withColumn("schema",  F.when(F.size(parts) >= 2, parts[1]))
        .withColumn("table",   F.when(F.size(parts) >= 3, parts[2]))
    )
  
-----------------------------------------------------------------------------------------------------------------------

# getting logs about tables - last build and rows count
dfs = []

for t in tables:
    df = spark.sql(f"""
        SELECT
            '{t}' AS path,
            COUNT(*) AS row_count,
            (
                SELECT MAX(date_format(from_utc_timestamp(timestamp, 'Europe/Warsaw'), 'yyyy-MM-dd HH:mm'))
                FROM (DESCRIBE HISTORY {t})
                WHERE operation IN ('CREATE OR REPLACE TABLE AS SELECT')
            ) AS last_rebuild_ts,
            date_format(from_utc_timestamp(current_timestamp(), 'Europe/Warsaw'), 'yyyy-MM-dd HH:mm') AS collected_ts
        FROM {t}
    """)
    dfs.append(df)
  
----------------------------------------------------------------------------------------------------------------------

# Current snapshot 
current_df = reduce(lambda a, b: a.unionByName(b), dfs) if dfs else None

----------------------------------------------------------------------------------------------------------------------

# Logic for deduplication if there is no change detected for each table separately

# Last snapshot for each table
w = Window.partitionBy("path").orderBy(F.col("collected_ts").desc())

latest_df = (
    spark.table("catalog.schema.monitoring_table")
    .withColumn("rn", F.row_number().over(w))
    .filter("rn = 1")  # only last snapshot
    .drop("rn")
)

# Comparing current snapshot with the last one
delta_df = (
    current_df.alias("c")
    .join(latest_df.alias("l"), "path", "left")
    .filter(
        (F.col("l.row_count").isNull()) |
        (F.col("c.row_count") != F.col("l.row_count")) |
        (F.col("c.last_rebuild_ts") != F.col("l.last_rebuild_ts"))
    )
    .select("c.*")  # Taking columns only from current snapshot
)

-------------------------------------------------------------------------------------------------------------------------

current_df = split_path(current_df)
delta_df = split_path(delta_df)

# Reordering columns after splitting fully qualified table name (path) to separate columns
ordered_columns = [
    "path",
    "catalog",
    "schema",
    "table",
    "row_count",
    "last_rebuild_ts",
    "collected_ts"
]

current_df = current_df.select(*ordered_columns)
delta_df = delta_df.select(*ordered_columns)

------------------------------------------------------------------------------------------------------------------------

table_exists = spark.catalog.tableExists("catalog.schema.monitoring_table")

if not table_exists:
    # First run so table catalog.schema.monitoring_table doesn't exist
    # Writing full current snapshot (current_df) and creating table
    current_df.write.mode("overwrite").saveAsTable("catalog.schema.monitoring_table")
    print("First run: table is created and full snapshot is written")
else:
    # Next runs so table catalog.schema.monitoring_table do exist
    # Writing only rows with different values (delta_df) by appending them to previous snapshot/s
    delta_df.write.mode("append").saveAsTable("catalog.schema.monitoring_table")
    print("Next run: only rows when change is detected versus previous row count per report are appended")
