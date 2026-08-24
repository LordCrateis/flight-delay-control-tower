"""PostgreSQL connection and aggregate-query helpers for the Dash dashboard.

Every public analytics function returns an already aggregated DataFrame. The
one-million-row flights table is never loaded into the Dash process.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


load_dotenv(Path(__file__).with_name(".env"))


class DashboardDatabaseError(RuntimeError):
    """Raised with a user-safe message when an aggregate query fails."""


def _database_url() -> str:
    configured = os.getenv("DATABASE_URL")
    if configured:
        return configured

    user = quote_plus(os.getenv("PGUSER", "postgres"))
    password = quote_plus(os.getenv("PGPASSWORD", ""))
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    database = os.getenv("PGDATABASE", "flights_db")
    credentials = f"{user}:{password}" if password else user
    return f"postgresql+psycopg2://{credentials}@{host}:{port}/{database}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(
        _database_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={"connect_timeout": 4, "application_name": "flight-delay-dashboard"},
    )


def _read(sql: str, params: dict | None = None) -> pd.DataFrame:
    try:
        with get_engine().connect() as connection:
            return pd.read_sql_query(text(sql), connection, params=params or {})
    except SQLAlchemyError as exc:
        raise DashboardDatabaseError(
            "PostgreSQL is unavailable. Check DATABASE_URL (or PGHOST, PGPORT, "
            "PGDATABASE, PGUSER, and PGPASSWORD), then refresh this page."
        ) from exc


def _airlines_tuple(airlines: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(sorted(a for a in (airlines or []) if a))


def _where(
    start_date: str,
    end_date: str,
    airlines: tuple[str, ...] = (),
    month: int | None = None,
) -> tuple[str, dict]:
    clauses = [
        '"FlightDate"::date BETWEEN CAST(:start_date AS date) AND CAST(:end_date AS date)'
    ]
    params: dict[str, object] = {"start_date": start_date, "end_date": end_date}

    if airlines:
        airline_params = []
        for index, airline in enumerate(airlines):
            key = f"airline_{index}"
            airline_params.append(f":{key}")
            params[key] = airline
        clauses.append(f'"Airline" IN ({", ".join(airline_params)})')

    if month:
        clauses.append('EXTRACT(MONTH FROM "FlightDate"::date) = :month')
        params["month"] = int(month)

    return " AND ".join(clauses), params


@lru_cache(maxsize=1)
def filter_metadata() -> dict:
    bounds = _read(
        """
        SELECT MIN("FlightDate"::date) AS min_date,
               MAX("FlightDate"::date) AS max_date
        FROM flights
        """
    ).iloc[0]
    airlines = _read(
        'SELECT DISTINCT "Airline" AS airline FROM flights ORDER BY airline'
    )["airline"].dropna().tolist()
    return {
        "min_date": str(bounds["min_date"]),
        "max_date": str(bounds["max_date"]),
        "airlines": airlines,
    }


@lru_cache(maxsize=1)
def filter_metadata_safe() -> tuple[dict, bool]:
    try:
        return filter_metadata(), True
    except DashboardDatabaseError:
        return {
            "min_date": "2022-01-01",
            "max_date": "2022-07-31",
            "airlines": [],
        }, False


@lru_cache(maxsize=128)
def overview_data(start_date: str, end_date: str, airlines: tuple[str, ...]):
    where, params = _where(start_date, end_date, airlines)
    kpis = _read(
        f"""
        SELECT COUNT(*)::bigint AS total_flights,
               100.0 * COUNT(*) FILTER (WHERE "ArrDelay" <= 15)
                   / NULLIF(COUNT("ArrDelay"), 0) AS on_time_pct,
               AVG("ArrDelay") AS avg_arr_delay,
               100.0 * COUNT(*) FILTER (WHERE "Cancelled")
                   / NULLIF(COUNT(*), 0) AS cancellation_rate
        FROM flights WHERE {where}
        """,
        params,
    )
    trend = _read(
        f"""
        SELECT DATE_TRUNC('month', "FlightDate"::date)::date AS month,
               AVG("ArrDelay") AS avg_arr_delay,
               100.0 * COUNT(*) FILTER (WHERE "ArrDelay" <= 15)
                   / NULLIF(COUNT("ArrDelay"), 0) AS on_time_pct,
               COUNT(*)::bigint AS flights
        FROM flights WHERE {where}
        GROUP BY 1 ORDER BY 1
        """,
        params,
    )
    airlines_worst = _read(
        f"""
        SELECT "Airline" AS label, AVG("ArrDelay") AS avg_delay,
               COUNT("ArrDelay")::bigint AS flights
        FROM flights WHERE {where} AND "ArrDelay" IS NOT NULL
        GROUP BY "Airline" HAVING COUNT("ArrDelay") >= 500
        ORDER BY avg_delay DESC LIMIT 5
        """,
        params,
    )
    airports_worst = _read(
        f"""
        SELECT "Origin" AS label, AVG("DepDelay") AS avg_delay,
               COUNT("DepDelay")::bigint AS flights
        FROM flights WHERE {where} AND "DepDelay" IS NOT NULL
        GROUP BY "Origin" HAVING COUNT("DepDelay") >= 500
        ORDER BY avg_delay DESC LIMIT 5
        """,
        params,
    )
    return kpis, trend, airlines_worst, airports_worst


@lru_cache(maxsize=256)
def carrier_metrics(
    start_date: str,
    end_date: str,
    airlines: tuple[str, ...],
    month: int | None,
) -> pd.DataFrame:
    where, params = _where(start_date, end_date, airlines, month)
    return _read(
        f"""
        SELECT "Airline" AS airline,
               COUNT(*)::bigint AS total_flights,
               AVG("ArrDelay") AS avg_delay,
               100.0 * COUNT(*) FILTER (WHERE "Cancelled")
                   / NULLIF(COUNT(*), 0) AS cancellation_rate,
               100.0 * COUNT(*) FILTER (WHERE "ArrDelay" <= 15)
                   / NULLIF(COUNT("ArrDelay"), 0) AS on_time_pct
        FROM flights WHERE {where}
        GROUP BY "Airline"
        ORDER BY avg_delay DESC NULLS LAST
        """,
        params,
    )


@lru_cache(maxsize=256)
def airport_metrics(
    start_date: str,
    end_date: str,
    airlines: tuple[str, ...],
    role: str,
    minimum_flights: int,
) -> pd.DataFrame:
    column = '"Dest"' if role == "destination" else '"Origin"'
    delay = '"ArrDelay"' if role == "destination" else '"DepDelay"'
    where, params = _where(start_date, end_date, airlines)
    params["minimum_flights"] = int(minimum_flights)
    return _read(
        f"""
        SELECT {column} AS airport,
               COUNT(*)::bigint AS total_flights,
               AVG({delay}) AS avg_delay,
               100.0 * COUNT(*) FILTER (WHERE "Cancelled")
                   / NULLIF(COUNT(*), 0) AS cancellation_rate,
               100.0 * COUNT(*) FILTER (WHERE "ArrDelay" <= 15)
                   / NULLIF(COUNT("ArrDelay"), 0) AS on_time_pct
        FROM flights WHERE {where}
        GROUP BY {column}
        HAVING COUNT(*) >= :minimum_flights
        ORDER BY avg_delay DESC NULLS LAST
        """,
        params,
    )


@lru_cache(maxsize=128)
def time_metrics(start_date: str, end_date: str, airlines: tuple[str, ...]):
    where, params = _where(start_date, end_date, airlines)
    hourly = _read(
        f"""
        SELECT FLOOR("CRSDepTime" / 100)::int AS hour,
               AVG("DepDelay") AS avg_delay,
               COUNT("DepDelay")::bigint AS flights
        FROM flights WHERE {where} AND "DepDelay" IS NOT NULL
        GROUP BY 1 ORDER BY 1
        """,
        params,
    )
    weekday = _read(
        f"""
        SELECT EXTRACT(DOW FROM "FlightDate"::date)::int AS day_index,
               TRIM(TO_CHAR("FlightDate"::date, 'Day')) AS day_name,
               AVG("DepDelay") AS avg_delay,
               COUNT("DepDelay")::bigint AS flights
        FROM flights WHERE {where} AND "DepDelay" IS NOT NULL
        GROUP BY 1, 2 ORDER BY 1
        """,
        params,
    )
    monthly = _read(
        f"""
        SELECT EXTRACT(MONTH FROM "FlightDate"::date)::int AS month_index,
               TO_CHAR("FlightDate"::date, 'Mon') AS month_name,
               AVG("DepDelay") AS avg_delay,
               100.0 * COUNT(*) FILTER (WHERE "Cancelled")
                   / NULLIF(COUNT(*), 0) AS cancellation_rate,
               COUNT(*)::bigint AS flights
        FROM flights WHERE {where}
        GROUP BY 1, 2 ORDER BY 1
        """,
        params,
    )
    return hourly, weekday, monthly


@lru_cache(maxsize=256)
def route_metrics(
    start_date: str,
    end_date: str,
    airlines: tuple[str, ...],
    minimum_flights: int,
) -> pd.DataFrame:
    where, params = _where(start_date, end_date, airlines)
    params["minimum_flights"] = int(minimum_flights)
    return _read(
        f"""
        SELECT "Origin" AS origin, "Dest" AS destination,
               "Origin" || ' → ' || "Dest" AS route,
               COUNT(*)::bigint AS total_flights,
               AVG("DepDelay") AS avg_delay,
               100.0 * COUNT(*) FILTER (WHERE "Cancelled")
                   / NULLIF(COUNT(*), 0) AS cancellation_rate,
               BOOL_OR("Origin" = 'EWR' OR "Dest" = 'EWR') AS involves_ewr
        FROM flights WHERE {where}
        GROUP BY "Origin", "Dest"
        HAVING COUNT(*) >= :minimum_flights
        """,
        params,
    )


def parse_filter_store(data: dict | None) -> tuple[str, str, tuple[str, ...]]:
    data = data or {}
    if data.get("start_date") and data.get("end_date"):
        return (
            data["start_date"],
            data["end_date"],
            _airlines_tuple(data.get("airlines")),
        )

    metadata, _ = filter_metadata_safe()
    return (
        data.get("start_date") or metadata["min_date"],
        data.get("end_date") or metadata["max_date"],
        _airlines_tuple(data.get("airlines")),
    )
