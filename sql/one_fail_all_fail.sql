-- Below it it simple 'if it's one fail then all fail' case -> assume you have multiple rows for one name (could be anything, e.g. card model) and couple of
-- validations per one car model in column car_attribute_validation. So let's assume we have 5 rows with the same car model and attribute_validation column with some Fail and Passed values.
-- The logic works the way that if there is at least one Fail for the same car model, whole car model gets 'Car model Has Not Passed Validation' in car_model_validation
-- flag. If all rows have Pass (below logic assumes everything except Fail is Pass) then whole car model gets 'Car model Has Passed Validation' flag.

SELECT
    base.*,
    CASE
      WHEN
        SUM(
          CASE
            WHEN car_attribute_validation = 'Fail' THEN 1
            ELSE 0
          END
        ) OVER (PARTITION BY car_model) > 0
      THEN 'Car model Has Not Passed Validation'
      ELSE 'Car model Has Passed Validation'
    END AS car_model_validation
  FROM
    base
