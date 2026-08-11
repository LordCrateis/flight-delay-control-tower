# Flight Delay Prediction Project

## Workflow
1. Download `Combined_Flights_2022.csv` from Kaggle, put it in `data/`
2. Subset it to the first 1M rows, check the date range isn't skewed to a few months
3. Generate the CREATE TABLE SQL from the CSV, load into Postgres
4. Clean it in SQL — nulls, dupes, weird values
5. Write ~20-30 SQL EDA queries — delay rates by carrier, airport, time, season, etc.
6. Python EDA — distributions, correlation, feature importance, drop useless columns
7. Train the model — predict delay risk/duration
8. Power BI dashboard
9. Build the control tower web app — input route, get back predicted delay risk
