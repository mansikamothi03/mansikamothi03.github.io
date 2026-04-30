"""
analyze.py
----------
Metric aggregation pipeline.
Reads raw product event CSV (Amplitude/Mixpanel/GA4 export format)
and computes key product metrics: DAU/WAU/MAU, feature adoption,
funnel conversion, retention, and top events.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any


def load_events(path: str = "data/sample_events.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["event_time"])
    print(f"Loaded {len(df):,} events from {path}")
    return df


def compute_dau_wau_mau(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute DAU, WAU, MAU and DAU/MAU stickiness ratio."""
    today = df["event_time"].max().date()
    day_start = pd.Timestamp(today)
    week_start = day_start - timedelta(days=6)
    month_start = day_start - timedelta(days=29)

    dau = df[df["event_time"].dt.date == today]["user_id"].nunique()
    wau = df[df["event_time"] >= week_start]["user_id"].nunique()
    mau = df[df["event_time"] >= month_start]["user_id"].nunique()

    return {
        "dau": dau,
        "wau": wau,
        "mau": mau,
        "dau_mau_ratio": round(dau / mau * 100, 1) if mau > 0 else 0,
        "as_of_date": str(today),
    }


def compute_feature_adoption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature adoption rate: % of MAU who used each feature at least once in last 30 days.
    """
    month_start = df["event_time"].max() - timedelta(days=29)
    recent = df[df["event_time"] >= month_start]
    mau = recent["user_id"].nunique()

    feature_events = recent[recent["event_type"].str.startswith("feature_")]
    adoption = (
        feature_events.groupby("event_type")["user_id"]
        .nunique()
        .reset_index()
        .rename(columns={"event_type": "feature", "user_id": "unique_users"})
    )
    adoption["adoption_rate_pct"] = (adoption["unique_users"] / mau * 100).round(1)
    adoption["feature"] = adoption["feature"].str.replace("feature_", "", regex=False)
    return adoption.sort_values("adoption_rate_pct", ascending=False).reset_index(drop=True)


def compute_funnel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trial-to-paid conversion funnel:
    signup → onboarding_start → first_value → trial_active → converted
    """
    funnel_steps = [
        "signup",
        "onboarding_start",
        "first_value_event",
        "trial_active",
        "converted_to_paid",
    ]

    month_start = df["event_time"].max() - timedelta(days=29)
    recent = df[df["event_time"] >= month_start]

    rows = []
    for step in funnel_steps:
        users = recent[recent["event_type"] == step]["user_id"].nunique()
        rows.append({"step": step, "users": users})

    funnel = pd.DataFrame(rows)
    funnel["drop_off_pct"] = (
        (1 - funnel["users"] / funnel["users"].shift(1)) * 100
    ).round(1)
    funnel["conversion_from_top_pct"] = (
        funnel["users"] / funnel["users"].iloc[0] * 100
    ).round(1)
    return funnel


def compute_top_events(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N events by volume in the last 30 days."""
    month_start = df["event_time"].max() - timedelta(days=29)
    recent = df[df["event_time"] >= month_start]
    return (
        recent.groupby("event_type")
        .agg(event_count=("event_id", "count"), unique_users=("user_id", "nunique"))
        .reset_index()
        .sort_values("event_count", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def compute_retention(df: pd.DataFrame, cohort_weeks: int = 8) -> pd.DataFrame:
    """
    Weekly cohort retention: % of users from signup week who returned in subsequent weeks.
    """
    df = df.copy()
    df["signup_week"] = df.groupby("user_id")["event_time"].transform("min").dt.to_period("W")
    df["event_week"] = df["event_time"].dt.to_period("W")
    df["weeks_since_signup"] = (df["event_week"] - df["signup_week"]).apply(lambda x: x.n)

    cohort_size = df.groupby("signup_week")["user_id"].nunique().rename("cohort_size")
    retention = (
        df[df["weeks_since_signup"] <= cohort_weeks]
        .groupby(["signup_week", "weeks_since_signup"])["user_id"]
        .nunique()
        .reset_index()
        .rename(columns={"user_id": "retained_users"})
    )
    retention = retention.merge(cohort_size, on="signup_week")
    retention["retention_rate_pct"] = (
        retention["retained_users"] / retention["cohort_size"] * 100
    ).round(1)
    return retention


def aggregate_all(path: str = "data/sample_events.csv") -> Dict[str, Any]:
    """Run all metric computations and return a structured dict."""
    df = load_events(path)
    return {
        "dau_wau_mau": compute_dau_wau_mau(df),
        "feature_adoption": compute_feature_adoption(df).to_dict(orient="records"),
        "funnel": compute_funnel(df).to_dict(orient="records"),
        "top_events": compute_top_events(df).to_dict(orient="records"),
    }


if __name__ == "__main__":
    import json
    metrics = aggregate_all()
    print("\n=== DAU / WAU / MAU ===")
    print(json.dumps(metrics["dau_wau_mau"], indent=2))
    print("\n=== Feature Adoption ===")
    print(pd.DataFrame(metrics["feature_adoption"]).to_string(index=False))
    print("\n=== Funnel ===")
    print(pd.DataFrame(metrics["funnel"]).to_string(index=False))
    print("\n=== Top Events ===")
    print(pd.DataFrame(metrics["top_events"]).to_string(index=False))