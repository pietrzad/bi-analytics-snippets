df = spark.table("catalog.schema.table") -- table to dump to csv

tmp_path = "dbfs:/FileStore/tmp_file_name"
final_path = "dbfs:/FileStore/file_name.csv"

(df
 .coalesce(1)                -- csv creation different options
 .write
 .mode("overwrite")
 .option("header", True)
 .option("sep", ",")
 .option("quote", '"')
 .option("quoteAll", True)
 .csv(tmp_path)
)

files = dbutils.fs.ls(tmp_path)
csv_file = [f.path for f in files if f.path.endswith(".csv")][0]

dbutils.fs.mv(csv_file, final_path, True)
dbutils.fs.rm(tmp_path, True)

print("CSV ready")
