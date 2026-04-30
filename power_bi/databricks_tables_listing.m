M query to list inside Power Query all tables from databricks

let
    Source = Databricks.Catalogs(
        "<databricks server>",
        "<http path (cluster)>"
    ),

    Catalog = Table.SelectRows(Source, each [Name] = "<Catalog>"){0}[Data],

    Database = Catalog{[Name="<Database>", Kind="Schema"]}[Data]
in
    Database
