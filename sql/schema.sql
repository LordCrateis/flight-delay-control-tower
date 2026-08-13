CREATE TABLE flights (
    "FlightDate" TEXT,
    "Airline" TEXT,
    "Origin" TEXT,
    "Dest" TEXT,
    "Cancelled" BOOLEAN,
    "Diverted" BOOLEAN,
    "CRSDepTime" INTEGER,
    "DepTime" DOUBLE PRECISION,
    "DepDelayMinutes" DOUBLE PRECISION,
    "DepDelay" DOUBLE PRECISION,
    "ArrTime" DOUBLE PRECISION,
    "ArrDelayMinutes" DOUBLE PRECISION,
    "AirTime" DOUBLE PRECISION,
    "CRSElapsedTime" DOUBLE PRECISION,
    "ActualElapsedTime" DOUBLE PRECISION,
    "Distance" DOUBLE PRECISION,
    "Year" INTEGER,
    "Quarter" INTEGER,
    "Month" INTEGER,
    "DayofMonth" INTEGER,
    "DayOfWeek" INTEGER,
    "Marketing_Airline_Network" TEXT,
    "Operated_or_Branded_Code_Share_Partners" TEXT,
    "DOT_ID_Marketing_Airline" INTEGER,
    "IATA_Code_Marketing_Airline" TEXT,
    "Flight_Number_Marketing_Airline" INTEGER,
    "Operating_Airline" TEXT,
    "DOT_ID_Operating_Airline" INTEGER,
    "IATA_Code_Operating_Airline" TEXT,
    "Tail_Number" TEXT,
    "Flight_Number_Operating_Airline" INTEGER,
    "OriginAirportID" INTEGER,
    "OriginAirportSeqID" INTEGER,
    "OriginCityMarketID" INTEGER,
    "OriginCityName" TEXT,
    "OriginState" TEXT,
    "OriginStateFips" INTEGER,
    "OriginStateName" TEXT,
    "OriginWac" INTEGER,
    "DestAirportID" INTEGER,
    "DestAirportSeqID" INTEGER,
    "DestCityMarketID" INTEGER,
    "DestCityName" TEXT,
    "DestState" TEXT,
    "DestStateFips" INTEGER,
    "DestStateName" TEXT,
    "DestWac" INTEGER,
    "DepDel15" DOUBLE PRECISION,
    "DepartureDelayGroups" DOUBLE PRECISION,
    "DepTimeBlk" TEXT,
    "TaxiOut" DOUBLE PRECISION,
    "WheelsOff" DOUBLE PRECISION,
    "WheelsOn" DOUBLE PRECISION,
    "TaxiIn" DOUBLE PRECISION,
    "CRSArrTime" INTEGER,
    "ArrDelay" DOUBLE PRECISION,
    "ArrDel15" DOUBLE PRECISION,
    "ArrivalDelayGroups" DOUBLE PRECISION,
    "ArrTimeBlk" TEXT,
    "DistanceGroup" INTEGER,
    "DivAirportLandings" INTEGER
);

-- OUTPUT
/* 
           List of relations
 Schema |  Name   | Type  |  Owner
--------+---------+-------+----------
 public | flights | table | postgres

 */



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