-- Selecting only rows with highest rank/any other attribute of any main id using QUALIFY function instead of window function, subquery and filtering

SELECT 
  name, 
  color, 
  (any other attribute column needed), 
  version 
FROM table
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY name                                  -- Partition amongst name (every name it's treated as a subset with highest version selected separately)
    ORDER BY CAST(version AS INT) DESC                 -- Casting in case our version/any other attribute we want filter only highest/lowest/whatever is text, not a number
) = 1
