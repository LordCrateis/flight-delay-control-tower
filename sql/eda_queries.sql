
-------------------------------------------------
------- CATEGORY 1 : CARRIER PERFORMANCE -------
-------------------------------------------------

-- Q1 What's the average departure delay by airline?

SELECT "Airline",
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY "Airline"
ORDER BY avg_dep_delay DESC;

/* OUTPUT
                  Airline                  | total_flights | avg_dep_delay
-------------------------------------------+---------------+---------------
 JetBlue Airways                           |         36735 |         26.20
 Frontier Airlines Inc.                    |         20663 |         20.10
 Allegiant Air                             |         17515 |         18.86
 GoJet Airlines, LLC d/b/a United Express  |          7883 |         17.06
 Spirit Air Lines                          |         30671 |         15.94
 Mesa Airlines Inc.                        |         16735 |         15.85
 American Airlines Inc.                    |        117126 |         14.81
 Southwest Airlines Co.                    |        175167 |         14.50
 United Air Lines Inc.                     |         84146 |         13.81
 Comair Inc.                               |         31840 |         12.94
 Commutair Aka Champlain Enterprises, Inc. |         10530 |         12.22
 Delta Air Lines Inc.                      |        122793 |         11.28
 SkyWest Airlines Inc.                     |        106092 |         11.26
 Republic Airlines                         |         45523 |         10.74
 Endeavor Air Inc.                         |         33654 |          9.77
 Air Wisconsin Airlines Corp               |          9710 |          8.22
 Envoy Air                                 |         35945 |          7.24
 Hawaiian Airlines Inc.                    |         10253 |          6.59
 Alaska Airlines Inc.                      |         30915 |          5.95
 Horizon Air                               |         13518 |          5.93
 Capital Cargo International               |         12815 |          5.87
(21 rows)

*/


-- Q2 What's the average arrival delay by airline?

SELECT "Airline",
       COUNT(*) AS total_flights,
       ROUND(AVG("ArrDelay")::numeric, 2) AS avg_arr_delay
FROM flights
WHERE "ArrDelay" IS NOT NULL
GROUP BY "Airline"
ORDER BY avg_arr_delay DESC;

/*OUTPUT
                  Airline                  | total_flights | avg_arr_delay
-------------------------------------------+---------------+---------------
 Allegiant Air                             |         17468 |         20.30
 JetBlue Airways                           |         36540 |         20.14
 Frontier Airlines Inc.                    |         20601 |         17.32
 GoJet Airlines, LLC d/b/a United Express  |          7854 |         12.89
 Spirit Air Lines                          |         30574 |         12.53
 Comair Inc.                               |         31697 |          9.67
 American Airlines Inc.                    |        116666 |          9.46
 Mesa Airlines Inc.                        |         16688 |          9.05
 Commutair Aka Champlain Enterprises, Inc. |         10493 |          8.11
 Southwest Airlines Co.                    |        174755 |          7.12
 Republic Airlines                         |         45269 |          7.03
 United Air Lines Inc.                     |         83858 |          6.70
 SkyWest Airlines Inc.                     |        105737 |          6.02
 Hawaiian Airlines Inc.                    |         10244 |          4.54
 Horizon Air                               |         13484 |          4.34
 Endeavor Air Inc.                         |         33526 |          4.01
 Delta Air Lines Inc.                      |        122496 |          3.84
 Alaska Airlines Inc.                      |         30795 |          3.26
 Envoy Air                                 |         35838 |          2.92
 Capital Cargo International               |         12755 |          2.58
 Air Wisconsin Airlines Corp               |          9688 |          2.09
(21 rows)
*/

-- Q3 What's the cancellation rate by airline?

SELECT "Airline",
       COUNT(*) AS total_flights,
       COUNT(*) FILTER (WHERE "Cancelled" = true) AS cancelled_flights,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Cancelled" = true) / COUNT(*), 2) AS cancellation_rate_pct
FROM flights
GROUP BY "Airline"
ORDER BY cancellation_rate_pct DESC;

/*OUTPUT

                  Airline                  | total_flights | cancelled_flights | cancellation_rate_pct
-------------------------------------------+---------------+-------------------+-----------------------
 GoJet Airlines, LLC d/b/a United Express  |          8463 |               592 |                  7.00
 Republic Airlines                         |         48220 |              2790 |                  5.79
 JetBlue Airways                           |         38544 |              1854 |                  4.81
 Mesa Airlines Inc.                        |         17448 |               722 |                  4.14
 Endeavor Air Inc.                         |         35049 |              1439 |                  4.11
 Comair Inc.                               |         33103 |              1309 |                  3.95
 Allegiant Air                             |         18211 |               703 |                  3.86
 American Airlines Inc.                    |        121648 |              4632 |                  3.81
 Commutair Aka Champlain Enterprises, Inc. |         10895 |               371 |                  3.41
 Air Wisconsin Airlines Corp               |         10039 |               334 |                  3.33
 Spirit Air Lines                          |         31687 |              1040 |                  3.28
 Frontier Airlines Inc.                    |         21279 |               632 |                  2.97
 Alaska Airlines Inc.                      |         31805 |               917 |                  2.88
 Capital Cargo International               |         13164 |               360 |                  2.73
 Envoy Air                                 |         36867 |               951 |                  2.58
 Southwest Airlines Co.                    |        179693 |              4555 |                  2.53
 United Air Lines Inc.                     |         86128 |              2021 |                  2.35
 SkyWest Airlines Inc.                     |        108336 |              2298 |                  2.12
 Delta Air Lines Inc.                      |        125325 |              2578 |                  2.06
 Horizon Air                               |         13758 |               253 |                  1.84
 Hawaiian Airlines Inc.                    |         10338 |                86 |                  0.83
(21 rows)


*/

-- Q4. Which airline has the highest % of on-time flights (delay ≤ 15 min, industry standard threshold)?

SELECT "Airline",
       COUNT(*) AS total_flights,
       COUNT(*) FILTER (WHERE "DepDelay" <= 15) AS on_time_flights,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "DepDelay" <= 15) / COUNT(*), 2) AS on_time_pct
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY "Airline"
ORDER BY on_time_pct DESC;

/*OUTPUT
                  Airline                  | total_flights | on_time_flights | on_time_pct
-------------------------------------------+---------------+-----------------+-------------
 Capital Cargo International               |         12815 |           11137 |       86.91
 Air Wisconsin Airlines Corp               |          9710 |            8346 |       85.95
 Endeavor Air Inc.                         |         33654 |           28848 |       85.72
 Horizon Air                               |         13518 |           11587 |       85.72
 Envoy Air                                 |         35945 |           30585 |       85.09
 Hawaiian Airlines Inc.                    |         10253 |            8682 |       84.68
 SkyWest Airlines Inc.                     |        106092 |           89570 |       84.43
 Alaska Airlines Inc.                      |         30915 |           25860 |       83.65
 Commutair Aka Champlain Enterprises, Inc. |         10530 |            8716 |       82.77
 Delta Air Lines Inc.                      |        122793 |          101326 |       82.52
 Republic Airlines                         |         45523 |           37192 |       81.70
 Mesa Airlines Inc.                        |         16735 |           13534 |       80.87
 Comair Inc.                               |         31840 |           25522 |       80.16
 United Air Lines Inc.                     |         84146 |           66457 |       78.98
 American Airlines Inc.                    |        117126 |           92200 |       78.72
 GoJet Airlines, LLC d/b/a United Express  |          7883 |            6151 |       78.03
 Spirit Air Lines                          |         30671 |           22977 |       74.91
 Southwest Airlines Co.                    |        175167 |          125503 |       71.65
 Frontier Airlines Inc.                    |         20663 |           14375 |       69.57
 Allegiant Air                             |         17515 |           12090 |       69.03
 JetBlue Airways                           |         36735 |           24274 |       66.08
(21 rows)

*/

--  Q5. Which airline has the most flights in this dataset (volume, for context — a carrier with 1 flight and 200min avg delay isn't meaningful)?

SELECT "Airline", COUNT(*) AS total_flights
FROM flights
GROUP BY "Airline"
ORDER BY total_flights DESC;

/*OUTPUT

                  Airline                  | total_flights 
-------------------------------------------+---------------
 Southwest Airlines Co.                    |        179693
 Delta Air Lines Inc.                      |        125325
 American Airlines Inc.                    |        121648
 SkyWest Airlines Inc.                     |        108336
 United Air Lines Inc.                     |         86128
 Republic Airlines                         |         48220
 JetBlue Airways                           |         38544
 Envoy Air                                 |         36867
 Endeavor Air Inc.                         |         35049
 Comair Inc.                               |         33103
 Alaska Airlines Inc.                      |         31805
 Spirit Air Lines                          |         31687
 Frontier Airlines Inc.                    |         21279
 Allegiant Air                             |         18211
 Mesa Airlines Inc.                        |         17448
 Horizon Air                               |         13758
 Capital Cargo International               |         13164
 Commutair Aka Champlain Enterprises, Inc. |         10895
 Hawaiian Airlines Inc.                    |         10338
 Air Wisconsin Airlines Corp               |         10039
 GoJet Airlines, LLC d/b/a United Express  |          8463
(21 rows)

*/

----------------------------------------
------- CATEGORY 2 : AIRPORTS --------
----------------------------------------

-- Q1.  What's the average departure delay by origin airport?

SELECT "Origin",
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY "Origin"
HAVING COUNT(*) > 500  -- filter out tiny airports with too few flights to be meaningful
ORDER BY avg_dep_delay DESC
LIMIT 20;

/*OUTPUT
 Origin | total_flights | avg_dep_delay
--------+---------------+---------------
 ASE    |           950 |         28.43
 PGD    |           983 |         25.12
 EYW    |          1260 |         23.92
 PBI    |          3503 |         23.20
 RAP    |           620 |         22.75
 JAC    |           604 |         21.90
 SRQ    |          2234 |         21.52
 FNT    |           506 |         21.15
 EWR    |         20058 |         20.89
 SJU    |          4238 |         20.84
 MDW    |          9796 |         20.32
 MCO    |         20218 |         19.85
 PWM    |          1519 |         19.56
 JFK    |         18455 |         19.24
 FLL    |         12184 |         18.99
 BWI    |         11436 |         18.69
 MIA    |         15723 |         18.32
 DEN    |         37297 |         18.22
 DRO    |           511 |         17.86
 RSW    |          5834 |         17.81
*/

-- Q2. What's the average arrival delay by destination airport?
SELECT "Dest",
       COUNT(*) AS total_flights,
       ROUND(AVG("ArrDelay")::numeric, 2) AS avg_arr_delay
FROM flights
WHERE "ArrDelay" IS NOT NULL
GROUP BY "Dest"
HAVING COUNT(*) > 500
ORDER BY avg_arr_delay DESC
LIMIT 20;

/*OUTPUT
Dest | total_flights | avg_arr_delay
------+---------------+---------------
 PGD  |           982 |         39.36
 PIE  |          1199 |         23.66
 SFB  |          1339 |         23.32
 ASE  |           972 |         22.50
 PBI  |          3666 |         19.12
 AZA  |           890 |         17.13
 PWM  |          1485 |         16.92
 MCO  |         20027 |         16.43
 ISP  |           799 |         16.16
 FNT  |           529 |         15.94
 EWR  |         19875 |         15.22
 SJU  |          4246 |         15.14
 FWA  |           863 |         14.77
 SRQ  |          2321 |         14.19
 HPN  |          1709 |         13.82
 RAP  |           620 |         13.67
 BDL  |          3258 |         13.30
 RSW  |          5785 |         13.18
 FAR  |           866 |         13.17
 FLL  |         12118 |         13.10
(20 rows)
*/

-- Which airports have the highest cancellation rate?
SELECT "Origin",
       COUNT(*) AS total_flights,
       COUNT(*) FILTER (WHERE "Cancelled" = true) AS cancelled_flights,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Cancelled" = true) / COUNT(*), 2) AS cancellation_rate_pct
FROM flights
GROUP BY "Origin"
HAVING COUNT(*) > 500
ORDER BY cancellation_rate_pct DESC
LIMIT 20;

/*OUTPUT
Origin | total_flights | cancelled_flights | cancellation_rate_pct
--------+---------------+-------------------+-----------------------
 ASE    |          1043 |                93 |                  8.92
 PWM    |          1639 |               123 |                  7.50
 LGA    |         24596 |              1579 |                  6.42
 EWR    |         21383 |              1358 |                  6.35
 BTV    |          1464 |                86 |                  5.87
 BGR    |           776 |                44 |                  5.67
 ROC    |          2338 |               128 |                  5.47
 DCA    |         21219 |              1124 |                  5.30
 FAI    |           687 |                36 |                  5.24
 HPN    |          1753 |                91 |                  5.19
 BUF    |          2962 |               152 |                  5.13
 PBI    |          3688 |               188 |                  5.10
 ALB    |          2141 |               104 |                  4.86
 JFK    |         19325 |               908 |                  4.70
 MHT    |          1022 |                48 |                  4.70
 ORF    |          3361 |               158 |                  4.70
 BDL    |          3326 |               156 |                  4.69
 PVD    |          2310 |               108 |                  4.68
 SYR    |          2305 |               106 |                  4.60
 PIA    |           529 |                24 |                  4.54
(20 rows)
*/

-- Q4. Which origin airports have the highest flight volume (busiest hubs)?

SELECT "Origin", COUNT(*) AS total_flights
FROM flights
GROUP BY "Origin"
ORDER BY total_flights DESC
LIMIT 20;

/*OUTPUT
 Origin | total_flights
--------+---------------
 ATL    |         45189
 ORD    |         42344
 DFW    |         39193
 DEN    |         38385
 CLT    |         30883
 LAX    |         27489
 LGA    |         24596
 SEA    |         24168
 LAS    |         23898
 PHX    |         23588
 EWR    |         21383
 IAH    |         21252
 DCA    |         21219
 MCO    |         20821
 BOS    |         19355
 JFK    |         19325
 DTW    |         18876
 SFO    |         18350
 MSP    |         17448
 MIA    |         16251
(20 rows)
*/

-- Q5. Do the busiest airports also have the worst delays, or is congestion not correlated with volume?
SELECT "Origin",
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY "Origin"
ORDER BY total_flights DESC
LIMIT 20;

/*OUTPUT
 Origin | total_flights | avg_dep_delay
--------+---------------+---------------
 ATL    |         44325 |         11.57
 ORD    |         41015 |         12.47
 DFW    |         37863 |         13.77
 DEN    |         37297 |         18.22
 CLT    |         29859 |         11.80
 LAX    |         27051 |         10.80
 SEA    |         23694 |          8.12
 LAS    |         23415 |         14.20
 PHX    |         23179 |         11.83
 LGA    |         23073 |         16.17
 IAH    |         20746 |         11.88
 MCO    |         20218 |         19.85
 DCA    |         20141 |         15.32
 EWR    |         20058 |         20.89
 BOS    |         18520 |         14.82
 JFK    |         18455 |         19.24
 DTW    |         18437 |         12.25
 SFO    |         18025 |          8.84
 MSP    |         17145 |         12.12
 MIA    |         15723 |         18.32
(20 rows)
*/

-----------------------------------------------------------------
----- CATEGORY 3 : TIME PATTERNS (SEASON, DAY, HOUR) -----
-----------------------------------------------------------------

-- Q1. What's the average delay by month (seasonality)?
SELECT EXTRACT(MONTH FROM "FlightDate") AS month,
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY month
ORDER BY month;

/*OUTPUT
 month | total_flights | avg_dep_delay
-------+---------------+---------------
     1 |        129745 |         11.12
     2 |        121834 |         11.38
     3 |        142663 |         12.49
     4 |        138913 |         13.25
     5 |        144787 |         12.46
     6 |        143083 |         15.90
     7 |        149204 |         14.65
(7 rows)
*/

-- Q2. What's the average delay by day of week?
SELECT TO_CHAR("FlightDate"::date, 'Day') AS day_of_week,
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY day_of_week, EXTRACT(DOW FROM "FlightDate"::date)
ORDER BY EXTRACT(DOW FROM "FlightDate"::date);

/*OUTPUT
 day_of_week | total_flights | avg_dep_delay
-------------+---------------+---------------
 Sunday      |        144375 |         15.00
 Monday      |        142865 |         13.14
 Tuesday     |        133999 |          8.94
 Wednesday   |        135798 |          9.47
 Thursday    |        142918 |         13.81
 Friday      |        143868 |         15.83
 Saturday    |        126406 |         15.34
(7 rows)
*/

-- Q3. What's the average delay by hour of scheduled departure (rush hour effect)?
SELECT FLOOR("CRSDepTime" / 100) AS scheduled_hour,
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY scheduled_hour
ORDER BY scheduled_hour;

/*OUTPUT
 scheduled_hour | total_flights | avg_dep_delay
----------------+---------------+---------------
              0 |          1991 |         15.94
              1 |           513 |         13.89
              2 |           230 |         17.65
              3 |           177 |          7.14
              4 |            84 |         20.08
              5 |         23885 |          5.30
              6 |         68399 |          5.67
              7 |         64694 |          6.07
              8 |         66594 |          6.77
              9 |         55623 |          7.81
             10 |         63372 |          8.92
             11 |         60405 |         10.40
             12 |         59172 |         11.04
             13 |         60038 |         12.94
             14 |         56367 |         14.55
             15 |         56451 |         15.93
             16 |         55206 |         17.06
             17 |         59995 |         18.40
             18 |         58066 |         19.23
             19 |         50367 |         21.78
             20 |         44523 |         21.46
             21 |         31398 |         21.57
             22 |         25101 |         20.36
             23 |          7578 |         17.49
(24 rows)
*/

-- Q4. Which month has the highest cancellation rate?
SELECT EXTRACT(MONTH FROM "FlightDate"::date) AS month,
       COUNT(*) AS total_flights,
       COUNT(*) FILTER (WHERE "Cancelled" = true) AS cancelled_flights,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Cancelled" = true) / COUNT(*), 2) AS cancellation_rate_pct
FROM flights
GROUP BY month
ORDER BY month;

/*OUTPUT
 month | total_flights | cancelled_flights | cancellation_rate_pct
-------+---------------+-------------------+-----------------------
     1 |        138584 |              8938 |                  6.45
     2 |        127414 |              5657 |                  4.44
     3 |        144803 |              2220 |                  1.53
     4 |        142015 |              3194 |                  2.25
     5 |        147684 |              2990 |                  2.02
     6 |        147562 |              4640 |                  3.14
     7 |        151938 |              2798 |                  1.84
(7 rows)
*/

-- Q5. Is there a difference between weekday and weekend delays?
SELECT CASE
         WHEN EXTRACT(DOW FROM "FlightDate"::date) IN (0, 6) THEN 'Weekend'
         ELSE 'Weekday'
       END AS day_type,
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY day_type;

/*OUTPUT
 day_type | total_flights | avg_dep_delay
----------+---------------+---------------
 Weekday  |        699448 |         12.31
 Weekend  |        270781 |         15.16
(2 rows)
*/

---------------------------------------------------
----- CATEGORY 4 : ROUTE-LEVEL ANALYSIS -----
---------------------------------------------------

-- Q1. What are the top 15 busiest routes (origin-destination pairs)?
SELECT "Origin", "Dest",
       COUNT(*) AS total_flights
FROM flights
GROUP BY "Origin", "Dest"
ORDER BY total_flights DESC
LIMIT 15;

/*OUTPUT
Origin | Dest | total_flights
--------+------+---------------
 ORD    | LGA  |          1661
 DCA    | BOS  |          1650
 SFO    | LAX  |          1649
 LGA    | ORD  |          1644
 BOS    | DCA  |          1595
 LAX    | SFO  |          1594
 LAX    | LAS  |          1494
 JFK    | LAX  |          1483
 LAS    | LAX  |          1453
 LAX    | JFK  |          1411
 HNL    | OGG  |          1378
 OGG    | HNL  |          1373
 LGA    | BOS  |          1255
 BOS    | LGA  |          1231
 ATL    | MCO  |          1146
(15 rows)
*/

-- Q2. Which routes have the worst average delay?
SELECT "Origin", "Dest",
       COUNT(*) AS total_flights,
       ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY "Origin", "Dest"
HAVING COUNT(*) > 200  -- filter out rare routes for statistical meaning
ORDER BY avg_dep_delay DESC
LIMIT 15;

/*OUTPUT
 Origin | Dest | total_flights | avg_dep_delay
--------+------+---------------+---------------
 SAV    | JFK  |           206 |         44.64
 RSW    | BOS  |           304 |         34.42
 JFK    | MCO  |           677 |         34.01
 HPN    | PBI  |           224 |         32.92
 LGA    | MCO  |           549 |         32.35
 PBI    | JFK  |           290 |         31.80
 BOS    | PBI  |           240 |         31.77
 JFK    | FLL  |           693 |         31.49
 LGA    | PBI  |           346 |         30.92
 FLL    | EWR  |           685 |         30.85
 FLL    | JFK  |           696 |         30.43
 JFK    | PBI  |           316 |         30.41
 EWR    | STL  |           216 |         30.04
 JFK    | ATL  |           427 |         29.64
 FLL    | BOS  |           409 |         29.49
(15 rows)
*/

-- Q3. Which routes have the highest cancellation rate?
SELECT "Origin", "Dest",
       COUNT(*) AS total_flights,
       COUNT(*) FILTER (WHERE "Cancelled" = true) AS cancelled_flights,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Cancelled" = true) / COUNT(*), 2) AS cancellation_rate_pct
FROM flights
GROUP BY "Origin", "Dest"
HAVING COUNT(*) > 200
ORDER BY cancellation_rate_pct DESC
LIMIT 15;

/*OUTPUT
 Origin | Dest | total_flights | cancelled_flights | cancellation_rate_pct
--------+------+---------------+-------------------+-----------------------
 ROC    | EWR  |           202 |                26 |                 12.87
 BNA    | EWR  |           328 |                42 |                 12.80
 PWM    | EWR  |           206 |                26 |                 12.62
 EWR    | BUF  |           223 |                28 |                 12.56
 EWR    | CMH  |           263 |                32 |                 12.17
 BUF    | EWR  |           210 |                25 |                 11.90
 DEN    | ASE  |           374 |                44 |                 11.76
 ASE    | DEN  |           352 |                41 |                 11.65
 DCA    | EWR  |           806 |                87 |                 10.79
 DCA    | PWM  |           207 |                22 |                 10.63
 EWR    | STL  |           240 |                25 |                 10.42
 CHO    | LGA  |           223 |                22 |                  9.87
 LGA    | CLE  |           470 |                46 |                  9.79
 ROC    | JFK  |           257 |                25 |                  9.73
 JFK    | ROC  |           247 |                24 |                  9.72
(15 rows)
*/

-- Q4. Does flight distance correlate with delay (short-haul vs long-haul)?
SELECT
  CASE
    WHEN "Distance" < 500 THEN 'Short-haul (<500mi)'
    WHEN "Distance" BETWEEN 500 AND 1500 THEN 'Medium-haul (500-1500mi)'
    ELSE 'Long-haul (>1500mi)'
  END AS haul_type,
  COUNT(*) AS total_flights,
  ROUND(AVG("DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights
WHERE "DepDelay" IS NOT NULL
GROUP BY haul_type
ORDER BY avg_dep_delay DESC;

/*OUTPUT
        haul_type         | total_flights | avg_dep_delay
--------------------------+---------------+---------------
 Medium-haul (500-1500mi) |        493388 |         14.41
 Long-haul (>1500mi)      |        113406 |         13.98
 Short-haul (<500mi)      |        363435 |         11.07
(3 rows)
*/

-- Q5. What's the average delay for the top 10 busiest routes specifically (busy ≠ necessarily bad, worth checking directly)?
WITH top_routes AS (
  SELECT "Origin", "Dest"
  FROM flights
  GROUP BY "Origin", "Dest"
  ORDER BY COUNT(*) DESC
  LIMIT 10
)
SELECT f."Origin", f."Dest",
       COUNT(*) AS total_flights,
       ROUND(AVG(f."DepDelay")::numeric, 2) AS avg_dep_delay
FROM flights f
JOIN top_routes t ON f."Origin" = t."Origin" AND f."Dest" = t."Dest"
WHERE f."DepDelay" IS NOT NULL
GROUP BY f."Origin", f."Dest"
ORDER BY total_flights DESC;

/*OUTPUT
 Origin | Dest | total_flights | avg_dep_delay 
--------+------+---------------+---------------
 SFO    | LAX  |          1631 |          8.15
 LAX    | SFO  |          1573 |          7.15
 ORD    | LGA  |          1551 |         16.98
 DCA    | BOS  |          1547 |         14.25
 LGA    | ORD  |          1539 |         15.33
 BOS    | DCA  |          1493 |         12.81
 LAX    | LAS  |          1479 |         12.30
 JFK    | LAX  |          1447 |         16.72
 LAS    | LAX  |          1438 |         12.20
 LAX    | JFK  |          1380 |         14.20
(10 rows)
*/
