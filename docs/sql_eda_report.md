# SQL EDA Report — Flight Delay Dataset (2022)

## Overview

- **Dataset**: 2022 US flight records, 1,000,000-row random sample (Kaggle "Flight Status Prediction" / BTS On-Time Performance data)
- **Sample coverage**: random sampling (seed=42), spans January–July 2022
- **Tool**: PostgreSQL (`flights_db.flights`, 61 columns)
- **Scope**: 20 business-question queries across 4 categories — Carrier Performance, Airports, Time Patterns, Route-Level Analysis

---

## Category 1: Carrier Performance

**Findings:**
- JetBlue Airways has the worst average departure delay (26.2 min), Horizon Air and Capital Cargo International the best (~5.9 min)
- Cancellation rate ranges widely: GoJet Airlines (7.0%) at the high end, Hawaiian Airlines (0.83%) at the low end
- On-time performance (≤15 min departure delay) ranges from 87% (Capital Cargo) down to 66% (JetBlue)
- No small-sample distortion — smallest carrier by volume still has 7,800+ flights

**Takeaway:** Delay and cancellation performance vary substantially by carrier, independent of flight volume. JetBlue and Frontier consistently rank worst across delay metrics; regional/legacy carriers (Horizon, Hawaiian, Alaska) consistently rank best.

---

## Category 2: Airports

**Findings:**
- Worst average departure delay: ASE (Aspen, 28.4 min), PGD, EYW, PBI also near the top
- Worst average arrival delay: PGD (39.4 min), PIE, SFB
- Highest cancellation rate: ASE (8.9%), PWM (7.5%), LGA and EWR both above 6%
- Busiest airports by volume: ATL, ORD, DFW, DEN, CLT
- **Volume does not predict delay.** ATL (busiest, 44K+ flights) has one of the lowest delays in the top 20 (11.6 min), while DEN (4th busiest) and EWR (mid-volume) rank among the worst (18.2 min and 20.9 min respectively)

**Takeaway:** Delay is airport-specific, not simply a function of traffic volume — infrastructure, regional weather, and airspace congestion matter more than raw flight count. EWR stands out as a recurring problem airport across multiple metrics.

---

## Category 3: Time Patterns

**Findings:**
- Seasonality: delay trends upward from January (11.1 min) through June (15.9 min) within the sampled range
- Day of week: Friday (15.8 min) and Sunday (15.0 min) worst; Tuesday (8.9 min) and Wednesday (9.5 min) best
- **Hour of day shows the strongest, cleanest pattern in the dataset**: delay climbs steadily from 5 AM (5.3 min) to a peak around 7–9 PM (~21–22 min), then drops off overnight
- Cancellation rate by month: January stands out sharply (6.45%) vs. all other months (1.5–4.4%), consistent with winter weather disruption
- Weekend flights average worse delays than weekday flights (15.2 min vs. 12.3 min)

**Takeaway:** Time-of-day is the single strongest delay predictor found in SQL EDA — delays compound through the day as the system falls behind schedule, resetting overnight. This is a strong candidate feature for the model.

*Note: the random sample covers January–July only; a full-year sample would be needed to confirm seasonal patterns beyond this range.*

---

## Category 4: Route-Level Analysis

**Findings:**
- Busiest routes: ORD↔LGA, DCA↔BOS, SFO↔LAX, LAX↔LAS all near 1,500+ flights in the sample
- Worst-delay routes are concentrated in the Northeast corridor and Florida leisure routes (SAV→JFK, RSW→BOS, JFK→MCO, LGA→MCO, JFK→FLL)
- Highest cancellation-rate routes are dominated by EWR (appears in 6 of the top 15), reinforcing EWR's problem-airport status from Category 2
- Distance vs. delay is non-linear: medium-haul routes (500–1,500 mi) are worst (14.4 min), short-haul best (11.1 min), long-haul in between (14.0 min)
- Busiest ≠ worst at the route level too: SFO↔LAX (highest volume) averages only 7–8 min delay, while ORD↔LGA (similar volume) averages 15–17 min

**Takeaway:** Delay concentrates on Northeast/Florida corridor routes and EWR-involved routes specifically, not simply high-traffic routes overall. Medium-haul distance is a mild risk factor, likely because it overlaps with the most congested corridors rather than distance itself driving delay.

---

## Cross-Category Observations

- **EWR appears repeatedly** as a problem airport: high average delay (Category 2), high cancellation rate (Category 2), and dominates the worst-cancellation route list (Category 4). Worth a dedicated "involves EWR" flag as a model feature.
- **Volume does not equal delay** at both the airport level (Category 2, Q5) and the route level (Category 4, Q5) — this rules out a naive "busier = worse" assumption and points to infrastructure/regional factors instead.
- **Time-of-day (Category 3) is the cleanest, most consistent pattern** found across all 20 queries — a near-monotonic climb through the day, dropping overnight.

## Data Note

This Kaggle subset does not include per-cause delay breakdown columns (`CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`, `LateAircraftDelay`) present in the full BTS dataset. Delay-cause analysis was not possible with this schema; delay composition (e.g. ground vs. air time via `TaxiOut`/`TaxiIn`) was left for the Python EDA phase.