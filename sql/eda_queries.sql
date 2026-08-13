---------------------------------------
--------- CARRIER PERFORMANCE --------- 
---------------------------------------

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