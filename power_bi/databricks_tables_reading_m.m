// this is standarized m code for power query with unified databricks source reading

let
    //table name to change in different queries
    TableName = "<table name>",

    //database connection
    SourceDb = Databricks.Catalogs(
        "<databricks workspace>",
        "<databricks compute>",
        [Catalog="<catalog>", Database=null, EnableAutomaticProxyDiscovery=null]
    ){[Name="<catalog>",Kind="Database"]}[Data],

    //SQL text
    SqlText =
    "SELECT * FROM <catalog>.<schema>." & TableName & "
     QUALIFY snapshot_date = MAX(snapshot_date) OVER () //extra code to get latest data using max snapshot date
    ",

    Source = Value.NativeQuery(
        SourceDb,
        SqlText,
        null,
        [EnableFolding=true]
    ),
