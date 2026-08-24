"""
train_model.py — Flight Delay Control Tower

Trains the final, locked-in delay-risk classifier and saves a single
deployable artifact bundle (model + encoders + feature contract).

This script reproduces ONLY the final, already-decided pipeline from the
EDA/modeling notebooks — no candidate comparison, no exploration. If you
want to re-run the exploration (historical-aggregate features vs
schedule-only, RandomForest vs LightGBM, etc.), do that in the notebooks,
not here.

Usage:
    python train_model.py --source postgres
    python train_model.py --source csv --csv-path ../data/flightsData1m.csv

Output:
    model/artifacts/risk_model.pkl   (single joblib bundle, see ARTIFACT
    below for exactly what it contains)
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split  # not used for the
# chronological split itself, kept only if a fallback random split is
# ever needed for debugging — the real split below is date-based.
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    classification_report,
)
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb


# ---------------------------------------------------------------------------
# Feature contract — this is the single source of truth for what the
# deployed API must send at inference time. If this list changes, the
# Control Tower app's /predict request body must change to match.
# ---------------------------------------------------------------------------

# Columns that are legitimately known BEFORE a flight departs.
NUMERIC_FEATURES = [
    "CRSDepTime",
    "CRSArrTime",
    "CRSElapsedTime",
    "Distance",
    "Month",
    "DayOfWeek",
    "DayofMonth",
    "sched_dep_hour",
    "sched_arr_hour",
    "sched_dep_minutes",
    "sched_arr_minutes",
    "dow_sin",
    "dow_cos",
    "dep_hour_sin",
    "dep_hour_cos",
    "arr_hour_sin",
    "arr_hour_cos",
    "log_distance",
    "planned_speed_mph",
]
CATEGORICAL_FEATURES = ["Airline", "Origin", "Dest", "route"]
FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TARGET = "risk_tier"
TARGET_LABELS = {0: "On-time", 1: "Minor delay", 2: "Severe delay"}

# Columns that must NEVER enter the feature set — outcome/leakage columns
# only known during or after a flight. This is enforced in code, not just
# documented, per the earlier leakage incident in this project.
FORBIDDEN_COLUMNS = {
    "DepDelay", "DepDelayMinutes", "DepDel15", "DepartureDelayGroups",
    "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups",
    "DepTime", "ArrTime", "TaxiOut", "TaxiIn", "WheelsOff", "WheelsOn",
    "AirTime", "ActualElapsedTime", "Cancelled", "Diverted",
    "DivAirportLandings",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_from_postgres(db_url: str) -> pd.DataFrame:
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    query = """
        SELECT "FlightDate", "CRSDepTime", "CRSArrTime", "CRSElapsedTime",
               "Distance", "Month", "DayOfWeek", "Airline", "Origin", "Dest",
               "ArrDelay", "Cancelled", "Diverted"
        FROM flights
    """
    df = pd.read_sql(query, engine)
    return df


def load_from_csv(path: str) -> pd.DataFrame:
    usecols = [
        "FlightDate", "CRSDepTime", "CRSArrTime", "CRSElapsedTime",
        "Distance", "Month", "DayOfWeek", "DayofMonth",
        "Airline", "Origin", "Dest",
        "ArrDelay", "Cancelled", "Diverted",
    ]
    df = pd.read_csv(path, usecols=usecols, low_memory=False)
    return df


# ---------------------------------------------------------------------------
# Feature engineering — mirrors the notebook exactly, kept in one place
# so training and future inference never drift apart.
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["FlightDate"] = pd.to_datetime(df["FlightDate"])

    # scheduled departure hour, cyclically encoded (0-23 -> sin/cos) so the
    # model sees hour 23 and hour 0 as close together, not far apart
    dep_hour = (df["CRSDepTime"] // 100).clip(0, 23)
    arr_hour = (df["CRSArrTime"] // 100).clip(0, 23)
    df["sched_dep_hour"] = dep_hour
    df["sched_arr_hour"] = arr_hour
    df["sched_dep_minutes"] = dep_hour * 60 + (df["CRSDepTime"] % 100)
    df["sched_arr_minutes"] = arr_hour * 60 + (df["CRSArrTime"] % 100)
    df["dow_sin"] = np.sin(2 * np.pi * df["DayOfWeek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["DayOfWeek"] / 7)
    df["dep_hour_sin"] = np.sin(2 * np.pi * dep_hour / 24)
    df["dep_hour_cos"] = np.cos(2 * np.pi * dep_hour / 24)
    df["arr_hour_sin"] = np.sin(2 * np.pi * arr_hour / 24)
    df["arr_hour_cos"] = np.cos(2 * np.pi * arr_hour / 24)
    df["log_distance"] = np.log1p(df["Distance"])
    df["planned_speed_mph"] = (
        df["Distance"] / (df["CRSElapsedTime"].replace(0, np.nan) / 60)
    )

    # route as a single categorical (Origin+Dest combined)
    df["route"] = df["Origin"] + "-" + df["Dest"]

    # outlier drop — matches the SQL-layer decision (DepDelay > 720 min).
    # ArrDelay is the target source here, so we mirror the same cutoff.
    df = df[(df["ArrDelay"].isna()) | (df["ArrDelay"] <= 720)]

    return df


def bucket_risk_tier(arr_delay: pd.Series) -> pd.Series:
    return pd.cut(
        arr_delay,
        bins=[-np.inf, 15, 60, np.inf],
        labels=[0, 1, 2],
    ).astype("Int64")


# ---------------------------------------------------------------------------
# Leakage guard — fails loudly rather than silently training on a
# forbidden column. This is the check that was missing in the first
# (leaky) model iteration on this project.
# ---------------------------------------------------------------------------

def assert_no_leakage(feature_cols):
    forbidden_present = [c for c in feature_cols if c in FORBIDDEN_COLUMNS]
    assert forbidden_present == [], (
        f"Leakage guard failed — forbidden outcome column(s) in feature "
        f"set: {forbidden_present}. These are only known during/after a "
        f"flight and must never be model inputs for a pre-flight "
        f"prediction. Fix FEATURE_COLS before training."
    )
    assert TARGET not in feature_cols, (
        f"Leakage guard failed — target column '{TARGET}' is in the "
        f"feature set."
    )


# ---------------------------------------------------------------------------
# Chronological split — train on earlier months, validate/test on later
# months, so evaluation simulates predicting genuinely future flights
# rather than randomly-interleaved ones.
# ---------------------------------------------------------------------------

def chronological_split(df: pd.DataFrame):
    train = df[df["FlightDate"] < pd.Timestamp("2022-06-01")]
    val = df[
        (df["FlightDate"] >= pd.Timestamp("2022-06-01"))
        & (df["FlightDate"] < pd.Timestamp("2022-07-01"))
    ]
    test = df[df["FlightDate"] >= pd.Timestamp("2022-07-01")]
    return train, val, test


# ---------------------------------------------------------------------------
# Encoding — label encoders are FIT ON TRAIN ONLY, then reused for
# val/test. Unseen categories at inference time (e.g. a route that never
# appeared in training) are mapped to a reserved "unknown" bucket rather
# than crashing.
# ---------------------------------------------------------------------------

UNKNOWN_TOKEN = "__unknown__"


def fit_encoders(train_df: pd.DataFrame) -> dict:
    encoders = {}
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        values = list(train_df[col].astype(str).unique()) + [UNKNOWN_TOKEN]
        le.fit(values)
        encoders[col] = le
    return encoders


def apply_encoders(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    df = df.copy()
    for col, le in encoders.items():
        known = set(le.classes_)
        safe_values = df[col].astype(str).where(
            df[col].astype(str).isin(known), UNKNOWN_TOKEN
        )
        df[col] = le.transform(safe_values)
    return df


def calibrated_predictions(
    model: lgb.LGBMClassifier,
    features: pd.DataFrame,
    train_priors: np.ndarray,
    gamma: float,
) -> np.ndarray:
    probabilities = model.predict_proba(features)
    return np.argmax(probabilities * (train_priors ** gamma), axis=1)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(args):
    print(f"Loading data from {args.source}...")
    if args.source == "postgres":
        df = load_from_postgres(args.db_url)
    else:
        df = load_from_csv(args.csv_path)
    print(f"Loaded {len(df):,} rows.")

    df = engineer_features(df)
    df[TARGET] = bucket_risk_tier(df["ArrDelay"])
    df = df.dropna(subset=[TARGET] + NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    df[TARGET] = df[TARGET].astype(int)

    assert_no_leakage(FEATURE_COLS)
    print(f"Leakage guard passed. Feature set ({len(FEATURE_COLS)}): {FEATURE_COLS}")

    train_df, val_df, test_df = chronological_split(df)
    print(
        f"Split sizes — train: {len(train_df):,} (Jan-May), "
        f"val: {len(val_df):,} (Jun), test: {len(test_df):,} (Jul)"
    )
    for name, part in [("train", train_df), ("val", val_df), ("test", test_df)]:
        if len(part) == 0:
            print(f"WARNING: {name} split is empty — check FlightDate range in source data.")

    encoders = fit_encoders(train_df)
    train_enc = apply_encoders(train_df, encoders)
    val_enc = apply_encoders(val_df, encoders)
    test_enc = apply_encoders(test_df, encoders)

    X_train, y_train = train_enc[FEATURE_COLS], train_enc[TARGET]
    X_val, y_val = val_enc[FEATURE_COLS], val_enc[TARGET]
    X_test, y_test = test_enc[FEATURE_COLS], test_enc[TARGET]
    train_counts = np.bincount(y_train.to_numpy(), minlength=3)
    train_priors = train_counts / train_counts.sum()

    print("Training LightGBM classifier...")
    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=3,
        class_weight="balanced",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        random_state=42,
        verbosity=-1,
    )
    model.fit(
        X_train,
        y_train,
        eval_X=X_val,
        eval_y=y_val,
        eval_metric="multi_logloss",
        callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)],
    )

    calibration_rows = []
    for gamma in np.linspace(0.0, 0.40, 41):
        val_pred = calibrated_predictions(model, X_val, train_priors, float(gamma))
        calibration_rows.append({
            "gamma": float(gamma),
            "accuracy": accuracy_score(y_val, val_pred),
            "balanced_accuracy": balanced_accuracy_score(y_val, val_pred),
            "macro_f1": f1_score(y_val, val_pred, average="macro"),
        })
    calibration = max(
        calibration_rows,
        key=lambda row: (row["macro_f1"], row["accuracy"]),
    )
    gamma = calibration["gamma"]
    print(
        "Validation-selected calibration — "
        f"gamma: {gamma:.2f}, accuracy: {calibration['accuracy']:.4f}, "
        f"balanced accuracy: {calibration['balanced_accuracy']:.4f}, "
        f"macro F1: {calibration['macro_f1']:.4f}"
    )

    print("\n--- Test set (July, unseen future month) ---")
    y_pred = calibrated_predictions(model, X_test, train_priors, gamma)
    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    print(f"Accuracy:          {acc:.4f}")
    print(f"Balanced accuracy: {bal_acc:.4f}")
    print(f"Macro F1:          {macro_f1:.4f}")
    print(classification_report(
        y_test, y_pred, target_names=[TARGET_LABELS[i] for i in range(3)]
    ))

    majority_baseline = y_test.value_counts(normalize=True).max()
    print(f"(Majority-class baseline for reference: {majority_baseline:.4f})")

    # -----------------------------------------------------------------
    # Save the deployable artifact bundle. Everything the Control Tower
    # API needs at inference time lives in this one file — the app
    # should never need to recompute encoders or guess the feature order.
    # -----------------------------------------------------------------
    artifact = {
        "model": model,
        "encoders": encoders,
        "feature_cols": FEATURE_COLS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_labels": TARGET_LABELS,
        "unknown_token": UNKNOWN_TOKEN,
        "train_priors": train_priors,
        "calibration_gamma": gamma,
        "trained_on": {
            "train_range": ["2022-01-01", "2022-05-31"],
            "val_range": ["2022-06-01", "2022-06-30"],
            "test_range": ["2022-07-01", "2022-07-31"],
        },
        "test_metrics": {
            "accuracy": acc,
            "balanced_accuracy": bal_acc,
            "macro_f1": macro_f1,
            "majority_baseline": float(majority_baseline),
        },
        "validation_metrics": calibration,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)
    print(f"\nSaved artifact bundle to {output_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=["postgres", "csv"], default="csv")
    p.add_argument(
        "--db-url",
        default="postgresql://localhost/flights_db",
        help="SQLAlchemy connection string, used when --source postgres",
    )
    p.add_argument(
        "--csv-path",
        default=str(Path(__file__).resolve().parent.parent / "data" / "flightsData1m.csv"),
        help="Path to the flights CSV, used when --source csv",
    )
    p.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent / "artifacts" / "risk_model.pkl"),
        help="Where to save the trained artifact bundle",
    )
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
