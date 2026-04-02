# Below code is for creating data profile in table

from pyspark.sql.functions import col, count, countDistinct, min, max, when, lit
from pyspark.sql import functions as F
 
# Compute total row count
df = df_source
total_rows = df.count()
 
# Compute profiling metrics for each column
profile_data = []
for col_name in df.columns:
    col_type = dict(df.dtypes)[col_name]  # Get column data type
   
    # Compute most frequent value and its count
    mode_df = df.groupBy(col_name).count().orderBy(F.desc("count")).limit(1)
    if mode_df.count() > 0:
        mode_row = mode_df.collect()[0]
        mode_value = mode_row[0]  # Most frequent value
        mode_count = mode_row[1]  # Count of most frequent value
    else:
        mode_value = None
        mode_count = 0
   
    profile_data.append(
        df.select(
            F.lit(col_name).alias("column_name"),  # Column name
            F.lit(col_type).alias("data_type"),  # Column type
            F.lit(total_rows).alias("total"), # Total rows
            F.count(col_name).alias("not null"), # Not null values
            F.countDistinct(col_name).alias("unique"), # unique values
            F.expr(f"ROUND(SUM(CASE WHEN {col_name} IS NULL THEN 1 ELSE 0 END) / {total_rows} * 100,2)").alias("empty %"),  # % of null values
            F.min(col_name).alias("min_value"), # min value
            F.max(col_name).alias("max_value"), # max mavlue
            F.lit(mode_value).alias("most_frequent_value"), # most frequent value
            F.lit(mode_count).alias("most_frequent_value_count")   # Count of most frequent value
        )
    )
 
# Combine results
profile_df = profile_data[0]
for i in range(1, len(profile_data)):
    profile_df = profile_df.union(profile_data[i])
 
# Show results
profile_df.display()
