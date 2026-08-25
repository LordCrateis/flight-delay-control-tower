<div align="center">

# Flight Delay Control Tower

**End-to-end delay analytics on a 1M-row sample of 2022 U.S. flights**

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-analysis-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LightGBM](https://img.shields.io/badge/LightGBM-classifier-9ACD32)](https://lightgbm.readthedocs.io/)
[![Plotly Dash](https://img.shields.io/badge/Plotly-Dash-3F4F75?logo=plotly&logoColor=white)](https://dash.plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/LICENSE)

</div>

---

An end-to-end flight-delay analytics project built around a one-million-row sample of 2022 U.S. flight records. The repository combines PostgreSQL data modeling, SQL exploratory analysis, Python EDA, a LightGBM delay-risk model, and a PostgreSQL-backed Plotly Dash dashboard for operational analysis.

The project is designed to help answer questions such as **which carriers, airports, time windows, and routes are most exposed to delays or cancellations**, and whether a planned flight should be classified as on time, a minor delay, or a severe delay.

> **Current implementation note.** The repository currently contains the data pipeline, model-training code and artifact, and the Dash analytics dashboard. The root `app/` directory is a placeholder; there is no separate prediction HTTP endpoint in the current tree. The dashboard queries PostgreSQL aggregates and does not load the trained model artifact by itself.

## Table of Contents

- [Project Objectives](#project-objectives)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Dataset](#dataset)
- [Database Schema](#database-schema)
- [Loading the Data](#loading-the-data)
- [Data-Quality Audit](#data-quality-audit)
- [SQL Exploratory Analysis](#sql-exploratory-analysis)
- [Python Exploratory Analysis](#python-exploratory-analysis)
- [Delay-Risk Model](#delay-risk-model)
- [Dashboard](#dashboard)
- [Dashboard Configuration](#dashboard-configuration)
- [End-to-End Local Setup](#end-to-end-local-setup)
- [Findings from the Current Analysis](#findings-from-the-current-analysis)
- [Important Caveats](#important-caveats)
- [Security and Operational Guidance](#security-and-operational-guidance)
- [Future Improvements](#future-improvements)
- [License](#license)
- [References](#references)

---

## Project Objectives

The project follows a practical analytics workflow:

1. Acquire and subset the 2022 flight dataset.
2. Load the data into PostgreSQL.
3. Audit nulls, duplicates, cancellations, diversions, and extreme delay values.
4. Explore carrier, airport, time, and route-level patterns in SQL and Python.
5. Train a leakage-safe pre-flight delay-risk classifier.
6. Package the model and feature contract into a deployable artifact.
7. Explore the results through an interactive Dash control-tower dashboard.

The repository's original project workflow is documented in the root README. [1]

## Architecture

```text
Combined_Flights_2022.csv
            │
            ▼
  notebooks/00_data_subsetting.ipynb
            │
            ▼
 data/flightsData1m.csv
            │
            ├──────────────────────┐
            ▼                      ▼
 PostgreSQL flights table      Python EDA notebook
            │                      │
            ├──────────────┐       │
            ▼              ▼       ▼
 SQL EDA queries      Dash dashboard   Feature/model analysis
            │              │       │
            └──────────────┴───────┘
                           │
                           ▼
              model/train_model.py
                           │
                           ▼
             model/artifacts/risk_model.pkl
```

The dashboard is intentionally query-driven. Its database layer returns already aggregated data, so the one-million-row `flights` table is not loaded into the Dash process. [9] [10]

## Technology Stack

| Layer | Technology |
| --- | --- |
| Data storage | PostgreSQL |
| SQL analysis | PostgreSQL SQL, aggregate queries, `psql`, `\copy` |
| Python analysis | Python, pandas, Polars, NumPy, scikit-learn, Matplotlib |
| Machine learning | LightGBM multiclass classifier, scikit-learn preprocessing and metrics |
| Dashboard | Plotly Dash, Dash Bootstrap Components, Plotly |
| Model serialization | Joblib |
| Configuration | `python-dotenv`, PostgreSQL URL or `PG*` environment variables |
| Deployment packaging | Docker-compatible Python application structure |

The project dependencies are declared in [`requirements.txt`](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/requirements.txt). [2]

## Repository Structure

```text
flight-delay-control-tower/
├── app/
│   └── .gitkeep                         # Placeholder for a future control-tower service
├── dashboard/
│   ├── app.py                           # Dash application shell
│   ├── db.py                            # PostgreSQL connection and aggregate queries
│   ├── .env.example                     # Dashboard configuration template
│   ├── README.md                        # Dashboard-specific run notes
│   ├── assets/
│   │   └── style.css                    # Dashboard styling
│   └── pages/
│       ├── overview.py                  # KPI overview and rankings
│       ├── carriers.py                  # Carrier comparison
│       ├── airports.py                  # Origin/destination analysis
│       ├── time_patterns.py             # Hour, weekday, and month patterns
│       ├── routes.py                    # Route and corridor analysis
│       ├── common.py                    # Shared dashboard helpers
│       └── __init__.py
├── docs/
│   ├── sql_eda_report.md                # Narrative findings from SQL EDA
│   └── pdfs/SQL EDA Report.pdf          # PDF version of the SQL report
├── model/
│   ├── artifacts/
│   │   └── risk_model.pkl               # Serialized model bundle
│   └── train_model.py                   # Training and artifact-generation script
├── notebooks/
│   ├── 00_data_subsetting.ipynb         # Dataset subsetting workflow
│   └── python_eda.ipynb                 # Python EDA and feature-selection analysis
├── sql/
│   ├── schema.sql                        # PostgreSQL flights table definition
│   ├── load_data.sql                     # Bulk CSV import command
│   ├── cleaning.sql                      # Data-quality audit queries
│   └── eda_queries.sql                   # 20 SQL business questions
├── .env.example                          # Root database URL template
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

The current repository tree does not include a committed `data/` directory or a Power BI `.pbix` file. The workflow references Power BI as a planned analysis output, but the tracked deliverables currently center on SQL, Python, the model artifact, and the Dash dashboard.

## Dataset

The analysis uses a one-million-row random sample of 2022 U.S. flight records derived from the Kaggle "Flight Status Prediction" / BTS On-Time Performance data. The sample was created with seed `42` and covers January through July 2022. The project documentation identifies the source scope and sample period. [7]

The raw source is expected to be named `Combined_Flights_2022.csv`. The subsetting notebook produces or supports the reduced file used by the PostgreSQL and model workflows:

```text
data/flightsData1m.csv
```

Create the local data directory and place the downloaded source file there before running the notebook:

```bash
mkdir -p data
# Place Combined_Flights_2022.csv in data/
```

Because the data contains flight records and operational fields, do not commit local copies unless redistribution rights and repository size constraints have been checked.

## Database Schema

The PostgreSQL schema creates one wide table named `flights` with 61 quoted BTS-style columns. These include:

- Flight date, carrier, origin, destination, cancellation, and diversion status.
- Scheduled and actual departure/arrival times.
- Departure and arrival delays.
- Scheduled and actual elapsed time, air time, taxi times, and distance.
- Carrier identifiers, airport identifiers, city and state metadata.
- Delay-group fields, time-block fields, and diversion-related fields.

Run the schema from the project root:

```bash
createdb flights_db
psql -d flights_db -f sql/schema.sql
```

The schema is a wide staging and analysis table rather than a normalized warehouse model. It currently defines no indexes, primary keys, foreign keys, or derived tables. [3]

## Loading the Data

The repository's load script expects the reduced CSV at `data/flightsData1m.csv`:

```bash
psql -d flights_db -f sql/load_data.sql
```

The script executes the following bulk load and row-count check:

```sql
\copy flights
FROM 'data/flightsData1m.csv'
WITH (FORMAT csv, HEADER true, NULL '');

SELECT COUNT(*) FROM flights;
```

If PostgreSQL cannot resolve the relative path, run the command from the project root or replace it with an absolute path. [4]

## Data-Quality Audit

Run the audit script after loading the table:

```bash
psql -d flights_db -f sql/cleaning.sql
```

The script checks for duplicate flight keys, missing delay values, canceled and diverted flights, and unusually large delay values. The recorded audit output includes 29,771 null departure delays, 32,974 null arrival delays, 30,437 canceled flights, and 2,537 diverted flights in the analyzed sample. The observed delay ranges include departure delays up to 7,223 minutes and arrival delays up to 7,232 minutes. [5]

This file is primarily an **audit script**, not a complete transformation pipeline. It reports problematic values and thresholds but does not update or delete rows. The model-training script applies its own outlier policy by excluding rows with `ArrDelay > 720` while preserving missing `ArrDelay` values until target creation.

## SQL Exploratory Analysis

The [`sql/eda_queries.sql`](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/sql/eda_queries.sql) file contains 20 business-question queries organized into four categories. [6]

| Category | Questions covered |
| --- | --- |
| Carrier performance | Average departure delay, average arrival delay, cancellation rate, on-time rate, and carrier volume. |
| Airport analysis | Worst origin departure delays, worst destination arrival delays, cancellation rates, busiest airports, and volume-versus-delay comparisons. |
| Time patterns | Delay by month, weekday, scheduled departure hour, monthly cancellation rate, and weekend-versus-weekday performance. |
| Route analysis | Busiest routes, worst-delay routes, highest-cancellation routes, distance buckets, and performance of the busiest routes. |

The SQL layer generally defines an on-time flight as one with a departure delay of **15 minutes or less**. Airport and route rankings use minimum-volume filters to reduce distortion from very small samples. The SQL file includes sample outputs alongside the queries for review and validation.

## Python Exploratory Analysis

[`notebooks/python_eda.ipynb`](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/notebooks/python_eda.ipynb) loads the one-million-row CSV with Polars and examines the structure and statistical behavior of the dataset. The notebook covers:

- Delay, taxi-time, and distance distributions.
- Skew and extreme-value inspection.
- Carrier, cancellation, and diversion counts.
- Class imbalance and missing-value behavior.
- Correlation among numeric columns.
- Redundant and unsuitable feature identification.
- Outlier review and the decision not to use post-departure values as pre-flight model inputs.

The notebook is an EDA and feature-selection stage; the final model is trained by [`model/train_model.py`](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/model/train_model.py). [8]

## Delay-Risk Model

The model predicts a three-class pre-flight risk tier from information known before departure:

| Class | Label | Definition from `ArrDelay` |
| --- | --- | --- |
| `0` | **On-time** | Arrival delay of 15 minutes or less. |
| `1` | **Minor delay** | More than 15 and up to 60 minutes late. |
| `2` | **Severe delay** | More than 60 minutes late. |

The target is created with `pd.cut` using the boundaries `[-∞, 15, 60, +∞]`. The model is a multiclass `lightgbm.LGBMClassifier` with balanced class weights.

### Pre-flight feature contract

The feature contract is explicitly defined in `model/train_model.py`. [8]

#### Numeric features

```text
CRSDepTime, CRSArrTime, CRSElapsedTime, Distance,
Month, DayOfWeek, DayofMonth,
sched_dep_hour, sched_arr_hour,
sched_dep_minutes, sched_arr_minutes,
dow_sin, dow_cos,
dep_hour_sin, dep_hour_cos,
arr_hour_sin, arr_hour_cos,
log_distance, planned_speed_mph
```

#### Categorical features

```text
Airline, Origin, Dest, route
```

The engineered features include scheduled departure and arrival hours, minute-of-day values, cyclical encodings for day and hour, log-transformed distance, planned speed, and a combined `Origin-Dest` route category.

### Leakage protection

The training code rejects outcome and post-departure columns through an explicit leakage guard. Forbidden fields include actual departure and arrival times, delay values, taxi times, wheels-off/wheels-on times, air time, actual elapsed time, cancellation, diversion, and other outcome-derived fields.

This is important because the deployed use case is a **pre-flight** risk estimate. A model that receives `ArrDelay`, `DepDelay`, or `Cancelled` as inputs would appear accurate while relying on information unavailable at prediction time.

### Chronological evaluation

The data is split by date rather than randomly interleaved:

| Split | Date range | Purpose |
| --- | --- | --- |
| Training | January 1–May 31, 2022 | Fit encoders and the classifier. |
| Validation | June 1–30, 2022 | Early stopping and calibration selection. |
| Test | July 1–31, 2022 | Evaluate on a future, unseen month. |

Categorical label encoders are fitted on the training split only. Unseen categories, such as a route not observed during training, are mapped to a reserved `__unknown__` bucket rather than causing inference to fail.

The classifier uses 500 estimators, a learning rate of `0.05`, 63 leaves, balanced class weights, and early stopping with a 30-round patience window. A validation-selected calibration parameter adjusts class predictions using training-class priors. [8]

### Train the model

The training script supports PostgreSQL and CSV sources:

```bash
# From a CSV file
python model/train_model.py \
  --source csv \
  --csv-path data/flightsData1m.csv

# From PostgreSQL
python model/train_model.py \
  --source postgres \
  --db-url postgresql://<user>:<password>@<host>:5432/flights_db
```

The default output path is:

```text
model/artifacts/risk_model.pkl
```

You can override it with `--output`:

```bash
python model/train_model.py \
  --source csv \
  --csv-path data/flightsData1m.csv \
  --output model/artifacts/risk_model.pkl
```

The serialized artifact contains the trained LightGBM model, categorical encoders, feature lists, target labels, the unknown-category token, class priors, calibration value, train/validation/test date ranges, and evaluation metrics.

## Dashboard

The current control-tower interface is the Plotly Dash application under `dashboard/`. It is an analytics-only dashboard backed by PostgreSQL. It queries aggregate results and returns only the smaller result sets needed for charts and tables.

Run it from the project root:

```bash
python dashboard/app.py
```

Open [http://127.0.0.1:8050](http://127.0.0.1:8050).

### Dashboard pages

| Route | Purpose |
| --- | --- |
| `/` | Overview KPIs, monthly reliability, worst carriers, and problem origin airports. |
| `/carriers` | Carrier comparison with average arrival delay, cancellation rate, and on-time performance. |
| `/airports` | Origin/destination analysis with minimum-volume filtering and sortable airport metrics. |
| `/time-patterns` | Delay by scheduled departure hour, weekday, and month with cancellation-rate context. |
| `/routes` | Busiest routes, worst-delay corridors, highest-cancellation corridors, and EWR-focused highlighting. |

The dashboard provides global date-range and airline filters, a PostgreSQL connection-status indicator, KPI cards for flights, on-time rate, average delay, and cancellations, and page-specific volume controls.

If PostgreSQL is unavailable, the dashboard displays a safe configuration state and uses the documented January 1–July 31, 2022 date range as a fallback for filter initialization. Query failures are converted into user-safe database errors rather than exposing raw connection details. [9] [10]

## Dashboard Configuration

Copy the dashboard environment template:

```bash
cp dashboard/.env.example dashboard/.env
```

Set either one complete SQLAlchemy URL:

```dotenv
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/flights_db
```

or configure PostgreSQL variables individually:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=flights_db
PGUSER=postgres
PGPASSWORD=<password>
```

Optional Dash settings are:

```dotenv
PORT=8050
DASH_DEBUG=false
```

The dashboard expects a PostgreSQL database named `flights_db` by default, a table named `flights`, and the quoted column names defined in `sql/schema.sql`. [10] [11]

> **Never commit credentials.** Do not commit `dashboard/.env` or any file containing a real database password. The root `.env.example` contains the same `DATABASE_URL` pattern for reference.

## End-to-End Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/LordCrateis/flight-delay-control-tower.git
cd flight-delay-control-tower

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate

# 3. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Create the local data directory
mkdir -p data

# 5. Place the source/subset CSV at:
#    data/flightsData1m.csv

# 6. Create the database and table
createdb flights_db
psql -d flights_db -f sql/schema.sql

# 7. Load the CSV and verify its row count
psql -d flights_db -f sql/load_data.sql

# 8. Run the data-quality audit
psql -d flights_db -f sql/cleaning.sql

# 9. Run the SQL analysis
psql -d flights_db -f sql/eda_queries.sql

# 10. Train or refresh the model artifact
python model/train_model.py \
  --source csv \
  --csv-path data/flightsData1m.csv

# 11. Configure and start the dashboard
cp dashboard/.env.example dashboard/.env
python dashboard/app.py
```

For a clean reproduction, run the dataset-subsetting notebook before the database-loading steps and confirm that the resulting file covers the intended January–July 2022 window rather than an accidentally skewed slice.

## Findings from the Current Analysis

The narrative report in [`docs/sql_eda_report.md`](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/docs/sql_eda_report.md) summarizes the current SQL findings. These figures are descriptive results for the repository's sampled data and should be recomputed if the dataset, sampling, filters, or SQL definitions change. [7]

| Area | Reported observation |
| --- | --- |
| Carrier performance | JetBlue has the highest average departure delay in the sample at 26.2 minutes; Capital Cargo has the highest reported on-time rate at 86.91%. |
| Cancellations | GoJet has the highest carrier cancellation rate at 7.00%; Hawaiian has the lowest at 0.83%. |
| Airports | ASE has the highest average origin departure delay among airports meeting the volume threshold; PGD has the highest average destination arrival delay. |
| Volume versus delay | The busiest airport is not automatically the worst-performing airport. ATL has high volume but comparatively low delay, while EWR and DEN rank worse on delay metrics. |
| Time of day | Average departure delay rises from the morning into the evening, reaching roughly 21–22 minutes around 7–9 PM in the sample. |
| Weekends | Weekend flights average 15.16 minutes of departure delay versus 12.31 minutes on weekdays. |
| Routes | The worst-delay routes are concentrated in Northeast and Florida corridors; EWR appears repeatedly among high-cancellation routes. |
| Distance | Medium-haul flights between 500 and 1,500 miles have the highest average departure delay among the three distance buckets. |

The report notes that this subset does not include the detailed delay-cause fields `CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`, and `LateAircraftDelay`, so cause-level attribution is outside the current analysis scope.

## Important Caveats

The analysis uses a random one-million-row sample covering only January through July 2022. It should not be treated as a complete annual or current operational view. Seasonal conclusions beyond the observed period require a full-year or multi-year dataset.

The risk model is evaluated on a future month within the same 2022 sample. This is stronger than a randomly interleaved split for simulating future prediction, but it is not a substitute for live production validation, drift monitoring, or out-of-time evaluation on later years.

The target is defined from arrival delay, while the features are restricted to pre-flight information. This makes the model appropriate for a pre-flight risk framing, but the predicted class is a statistical risk tier rather than a guaranteed outcome.

The current dashboard and model are separate runtime components. The Dash application reads PostgreSQL aggregates and does not call `risk_model.pkl`. A production control tower that displays route-level predictions would need a serving layer or an explicit model-inference integration between the dashboard and the artifact.

## Security and Operational Guidance

Store database credentials in environment variables or a secret manager. Never commit `dashboard/.env`, passwords, or private connection strings.

Keep model artifacts versioned with their feature contract and training metadata. The `risk_model.pkl` file is a joblib-serialized Python object and should only be loaded from a trusted source.

Before public deployment, add authentication or network controls, HTTPS, request validation, rate limiting, structured logging, database indexes, and health checks. The current dashboard is intended for trusted or controlled environments and has no user authentication layer.

The current PostgreSQL schema has no indexes. For larger datasets or production workloads, add indexes that match the dashboard's date, airline, origin, destination, and route aggregations, then validate query plans before enabling aggressive caching.

## Future Improvements

The most valuable next steps are to add a dedicated `/predict` service that loads `risk_model.pkl`, connect the dashboard route page to model inference, add a production-ready deployment configuration, introduce automated data-quality tests, version the dataset sample, add model explainability, and include a real Power BI artifact only if it remains part of the intended deliverable.

A data dictionary would also improve maintainability by documenting every source column, units, null behavior, delay threshold, date convention, and distinction between departure and arrival metrics.

## License

This project is distributed under the [MIT License](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/LICENSE). [12]

## References

1. [Flight Delay Control Tower project workflow](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/README.md)
2. [Flight Delay Control Tower Python dependencies](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/requirements.txt)
3. [PostgreSQL flights table schema](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/sql/schema.sql)
4. [PostgreSQL CSV loading script](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/sql/load_data.sql)
5. [Flight data-quality audit queries](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/sql/cleaning.sql)
6. [Flight delay SQL exploratory analysis](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/sql/eda_queries.sql)
7. [Flight delay SQL EDA report](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/docs/sql_eda_report.md)
8. [Flight delay-risk model training script](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/model/train_model.py)
9. [Flight Delay Dash application shell](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/dashboard/app.py)
10. [Dashboard PostgreSQL and aggregate-query layer](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/dashboard/db.py)
11. [Dashboard environment configuration template](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/dashboard/.env.example)
12. [Flight Delay Control Tower MIT License](https://github.com/LordCrateis/flight-delay-control-tower/blob/main/LICENSE)
