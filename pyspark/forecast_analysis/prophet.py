import time
from prophet import Prophet
import logging
import contextlib
import sys
import os
from pyspark.sql.functions import col, to_date
import pandas as pd

# Set cmdstanpy logger to ERROR to suppress INFO messages
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)

# Optional: also suppress Prophet logs if needed
logging.getLogger("prophet").setLevel(logging.ERROR)

# Disable CMDSTANPY logging to file if used
os.environ['CMDSTANPY_LOG'] = 'False'

# Optional helper to suppress stdout temporarily
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as fnull:
        old_stdout = sys.stdout
        sys.stdout = fnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

------------------------------------------------------------------------------------------------------------------------------------------------------------

# Select Data
query = f"""
    SELECT DISTINCT
       measure_id
      ,sub_pillar
      ,sub_sector
      ,site_name
      ,period_start_date
      ,SUM(measure_qty) AS measure_qty
    FROM table
  """

df = spark.sql(query)

------------------------------------------------------------------------------------------------------------------------------------------------------

# Prepare Data

# Check total number of combinations
combinations = df.select("measure_id", "sub_sector", "site_name").distinct().collect()
print(f"Count of all distinct combinations: {len(combinations)}")

def forecast_for_combination(measure_id, sub_sector, site_name, df):
    df_filtered = df.filter((col("measure_id") == measure_id) & (col("sub_sector") == sub_sector) & (col("site_name") == site_name))

    train_df = df_filtered.select(
        to_date(col("period_start_date")).alias("ds"),
        col("measure_id"),
        col("measure_qty").alias("y").cast("double")
    ).orderBy(col("ds").desc())

    history_pd = train_df.toPandas()

    if history_pd.shape[0] < 2:
        print(f"Skipping measure_id: {measure_id}, sub_sector: {sub_sector}, site_name: {site_name} - Not enough data points.")
        return None  # Not enough data
      
----------------------------------------------------------------------------------------------------------------------------------------------------

# Prophet Settings

    model = Prophet(
        interval_width=0.95,
        growth='linear',
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False,
        seasonality_mode='additive'
    )

    model.fit(history_pd, iter=1000)

    future_pd = model.make_future_dataframe(
        periods=3, 
        freq='q', 
        include_history=True
        )
    
    forecast_pd = model.predict(future_pd)

    forecast_pd = forecast_pd[["ds", "yhat", "yhat_lower", "yhat_upper", "trend"]].rename(columns={
        "ds": "date",
        "yhat": "predicted_value",
        "yhat_lower": "lower_bound",
        "yhat_upper": "upper_bound",
        "trend": "trend"
    })

    forecast_pd["measure_id"] = measure_id
    forecast_pd["sub_sector"] = sub_sector
    forecast_pd["site_name"] = site_name

    return forecast_pd[["measure_id", "sub_sector", "site_name", "date", "predicted_value", "lower_bound", "upper_bound", "trend"]]
  
---------------------------------------------------------------------------------------------------------------------------------------------------------

# Data Processing Part

# Loop with timing and logging
all_forecasts = []

total_combinations = len(combinations)
overall_start = time.time()

for idx, row in enumerate(combinations):
    start_time = time.time()
    measure_id = row["measure_id"]
    sub_sector = row["sub_sector"]
    site_name = row["site_name"]

    try:
        result = forecast_for_combination(measure_id, sub_sector, site_name, df)
        if result is not None:
            all_forecasts.append(result)
        elapsed_time = time.time() - start_time
        processed = idx + 1
        remaining = total_combinations - processed
        percent_complete = (processed / total_combinations) * 100
        total_seconds = int(time.time() - overall_start)
        minutes, seconds = divmod(total_seconds, 60)

        print(f"Processed {processed}/{total_combinations} ({percent_complete:.1f}%) - measure_id: {measure_id}, sub_sector: {sub_sector}, site_name: {site_name}, "
              f"elapsed time: {elapsed_time:.2f}s, total time: {minutes}m {seconds}s, remaining: {remaining}")
    except Exception as e:
        print(f"Error processing measure_id: {measure_id}, sub_sector: {sub_sector}, site_name: {site_name} — {str(e)}")

----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Merge and display
if all_forecasts:
    final_forecast_pd = pd.concat(all_forecasts, ignore_index=True)
    forecast_spark_df = spark.createDataFrame(final_forecast_pd)
    display(forecast_spark_df)
else:
    print("No forecasts to display.")
