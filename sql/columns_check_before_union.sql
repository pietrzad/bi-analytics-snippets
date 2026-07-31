-- Query to compare columns structure in tables before union

WITH tables_to_compare AS (
    SELECT '<table name>' AS table_name UNION ALL
    SELECT '<table name>' UNION ALL
    SELECT '<table name>'
),

table_count AS (
    SELECT COUNT(*) AS expected_tables
    FROM tables_to_compare
),

columns AS (
    SELECT
        c.table_name,
        c.ordinal_position,
        c.column_name,
        c.data_type
    FROM <catalog name>.information_schema.columns c
    JOIN tables_to_compare t
        ON c.table_name = t.table_name
    WHERE c.table_schema = '<schema name>'
)

SELECT
    ordinal_position,

    COUNT(DISTINCT table_name) AS found_in_tables,

    (SELECT expected_tables FROM table_count) AS expected_tables,

    CASE
        WHEN COUNT(DISTINCT table_name) < (SELECT expected_tables FROM table_count)
            THEN 'MISSING'

        WHEN SIZE(
                COLLECT_SET(
                    CONCAT(column_name, ':', data_type)
                )
             ) > 1
            THEN 'COLUMN_MISMATCH'

        ELSE 'OK'
    END AS schema_status,

    array_join(
        sort_array(
            collect_set(table_name)
        ),
        ', '
    ) AS tables,

    array_join(
        sort_array(
            collect_set(
                CONCAT(column_name, ':', data_type)
            )
        ),
        ', '
    ) AS definitions

FROM columns

GROUP BY ordinal_position

ORDER BY ordinal_position;
