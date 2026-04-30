"""
analyze.py
----------
Load and analyze the Zendesk ticket dataset.
Produces summary tables for: volume by category, agent performance,
CSAT trends, SLA compliance, and weekly ticket volume trends.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams["figure.dpi"] = 150


def load_tickets(path: str = "data/raw/tickets.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["created_at", "solved_at", "first_reply_at"])
    print(f"Loaded {len(df)} tickets from {path}")
    return df


def volume_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Ticket volume, SLA breach rate, and avg resolution time by category."""
    result = (
        df.groupby("category")
        .agg(
            total_tickets=("ticket_id", "count"),
            sla_breaches=("is_sla_breached", "sum"),
            avg_resolution_hours=("resolution_hours", "mean"),
            median_resolution_hours=("resolution_hours", "median"),
            csat_good=("csat_score", lambda x: (x == "good").sum()),
            csat_bad=("csat_score", lambda x: (x == "bad").sum()),
        )
        .reset_index()
    )
    result["pct_of_total"] = (result["total_tickets"] / result["total_tickets"].sum() * 100).round(1)
    result["sla_breach_rate_pct"] = (result["sla_breaches"] / result["total_tickets"] * 100).round(1)
    result["csat_pct"] = (
        result["csat_good"] / (result["csat_good"] + result["csat_bad"]) * 100
    ).round(1)
    result["avg_resolution_hours"] = result["avg_resolution_hours"].round(1)
    return result.sort_values("total_tickets", ascending=False).reset_index(drop=True)


def agent_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Agent-level metrics: volume, resolution time, CSAT, SLA compliance."""
    solved = df[df["status"].isin(["solved", "closed"])].copy()
    result = (
        solved.groupby("agent")
        .agg(
            tickets_handled=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
            avg_first_reply_hours=("first_reply_hours", "mean"),
            sla_breaches=("is_sla_breached", "sum"),
            csat_good=("csat_score", lambda x: (x == "good").sum()),
            csat_bad=("csat_score", lambda x: (x == "bad").sum()),
        )
        .reset_index()
    )
    result["sla_compliance_pct"] = (
        (1 - result["sla_breaches"] / result["tickets_handled"]) * 100
    ).round(1)
    result["csat_pct"] = (
        result["csat_good"] / (result["csat_good"] + result["csat_bad"]) * 100
    ).round(1)
    result["avg_resolution_hours"] = result["avg_resolution_hours"].round(1)
    return result.sort_values("csat_pct", ascending=False).reset_index(drop=True)


def weekly_volume_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Weekly ticket volume trend with 4-week rolling average."""
    df = df.copy()
    df["week"] = df["created_at"].dt.to_period("W").dt.start_time
    weekly = df.groupby("week").agg(tickets=("ticket_id", "count")).reset_index()
    weekly["rolling_4w"] = weekly["tickets"].rolling(4, min_periods=1).mean().round(1)
    return weekly


def plot_volume_by_category(vol: pd.DataFrame, save_path: str = None) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Volume bar
    axes[0].barh(vol["category"], vol["total_tickets"], color="#a78bfa", alpha=0.85)
    axes[0].set_xlabel("Ticket Count")
    axes[0].set_title("Ticket Volume by Category (Last 90 Days)")
    axes[0].invert_yaxis()
    for i, (v, p) in enumerate(zip(vol["total_tickets"], vol["pct_of_total"])):
        axes[0].text(v + 2, i, f"{p}%", va="center", fontsize=8)

    # SLA breach rate
    colors = ["#fc8181" if r > 20 else "#34d399" for r in vol["sla_breach_rate_pct"]]
    axes[1].barh(vol["category"], vol["sla_breach_rate_pct"], color=colors, alpha=0.85)
    axes[1].set_xlabel("SLA Breach Rate (%)")
    axes[1].set_title("SLA Breach Rate by Category")
    axes[1].invert_yaxis()
    axes[1].axvline(x=20, color="white", linestyle="--", alpha=0.4, label="20% threshold")
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved: {save_path}")
    else:
        plt.show()


def plot_weekly_trend(weekly: pd.DataFrame, save_path: str = None) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(weekly["week"], weekly["tickets"], color="#63b3ed", alpha=0.5, label="Weekly tickets")
    ax.plot(weekly["week"], weekly["rolling_4w"], color="#a78bfa", linewidth=2, label="4-week rolling avg")
    ax.set_xlabel("Week")
    ax.set_ylabel("Ticket Count")
    ax.set_title("Weekly Ticket Volume Trend")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved: {save_path}")
    else:
        plt.show()


def print_summary(df: pd.DataFrame, vol: pd.DataFrame, agent: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("  ZENDESK SUPPORT ANALYTICS — SUMMARY")
    print("=" * 60)
    print(f"\nTotal tickets: {len(df):,}")
    print(f"Date range: {df['created_at'].min().date()} → {df['created_at'].max().date()}")
    print(f"SLA breach rate: {df['is_sla_breached'].mean()*100:.1f}%")
    csat_df = df[df["csat_score"].notna()]
    print(f"Overall CSAT: {(csat_df['csat_score']=='good').mean()*100:.1f}%")
    print(f"\nTop category by volume: {vol.iloc[0]['category']} ({vol.iloc[0]['pct_of_total']}%)")
    print(f"Highest SLA breach rate: {vol.sort_values('sla_breach_rate_pct', ascending=False).iloc[0]['category']}")
    print(f"\nTop agent by CSAT: {agent.iloc[0]['agent']} ({agent.iloc[0]['csat_pct']}%)")
    print("=" * 60)


if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    df = load_tickets()
    vol = volume_by_category(df)
    agent = agent_performance(df)
    weekly = weekly_volume_trend(df)

    print_summary(df, vol, agent)

    print("\n--- Volume by Category ---")
    print(vol[["category", "total_tickets", "pct_of_total", "sla_breach_rate_pct", "csat_pct"]].to_string(index=False))

    print("\n--- Agent Performance ---")
    print(agent[["agent", "tickets_handled", "avg_resolution_hours", "sla_compliance_pct", "csat_pct"]].to_string(index=False))

    # Export
    vol.to_csv("data/processed/volume_by_category.csv", index=False)
    agent.to_csv("data/processed/agent_performance.csv", index=False)
    weekly.to_csv("data/processed/weekly_trend.csv", index=False)

    # Plots
    plot_volume_by_category(vol, save_path="outputs/volume_by_category.png")
    plot_weekly_trend(weekly, save_path="outputs/weekly_trend.png")

    print("\n✅ Analysis complete. Outputs saved to data/processed/ and outputs/")