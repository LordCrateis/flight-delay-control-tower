

-- Duplicate values check
SELECT "FlightDate", "Airline", "Origin", "Dest", "CRSDepTime", COUNT(*)
FROM flights
GROUP BY "FlightDate", "Airline", "Origin", "Dest", "CRSDepTime"
HAVING COUNT(*) > 1;


-- Null Audit 
SELECT
  COUNT(*) FILTER (WHERE "DepDelay" IS NULL) AS null_depdelay,
  COUNT(*) FILTER (WHERE "ArrDelay" IS NULL) AS null_arrdelay,
  COUNT(*) FILTER (WHERE "Cancelled" = true) AS cancelled_count,
  COUNT(*) FILTER (WHERE "Diverted" = true) AS diverted_count
FROM flights;

-- Output
/*
 null_depdelay | null_arrdelay | cancelled_count | diverted_count
---------------+---------------+-----------------+----------------
         29771 |         32974 |           30437 |           2537
(1 row)
*/

-- Impossible/bad values check

SELECT MIN("DepDelay"), MAX("DepDelay"), MIN("ArrDelay"), MAX("ArrDelay")
FROM flights;

-- Output

/*
 min | max  | min | max
-----+------+-----+------
 -55 | 7223 | -81 | 7232
(1 row)
*/

-- Checking thresholds to keep in mind
SELECT COUNT(*) FROM flights WHERE "DepDelay" > 1440; -- more than 24 hours
SELECT COUNT(*) FROM flights WHERE "DepDelay" > 720;  -- more than 12 hours