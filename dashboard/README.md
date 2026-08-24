# Flight Delay Analytics Dashboard

Analytics-only Plotly Dash application backed by PostgreSQL. All summary data is aggregated in SQL; the one-million-row `flights` table is never loaded into the web process.

## Run locally

1. Install the root dependencies: `pip install -r requirements.txt`
2. Copy `dashboard/.env.example` to `dashboard/.env` and set the PostgreSQL credentials.
3. From the project root, run `python dashboard/app.py`.
4. Open `http://127.0.0.1:8050`.

The app expects database `flights_db`, table `flights`, and the quoted BTS column names defined in `sql/schema.sql`.
