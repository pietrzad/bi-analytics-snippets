WITH MAPPING AS (
      SELECT
        MAP(
          'laptop', 'computer', -- laptop change to computer
          'vehicle', 'car',  -- vehicle change to car
        ) AS thing_map
      ),
      DATA AS (
        SELECT DISTINCT
          columnA, --other column
          columnB, --other column
      
          -- map usage when 'laptop' and 'vehicle' are atomic values in column
          COALESCE(ELEMENT_AT(thing_map, LOWER(columnC)), columnC) AS columnC,
      
          -- map usage when 'laptop' and 'vehicle' are part of free text column and could be inside a sentence/longer text
          AGGREGATE(
            MAP_ENTRIES(thing_map),
            columnD,
            (acc, x) -> REGEXP_REPLACE(acc, CONCAT('(?i)\\b', x.key, '\\b'), x.value)
          ) AS columnD
      
        FROM
          data 
          CROSS JOIN mapping
