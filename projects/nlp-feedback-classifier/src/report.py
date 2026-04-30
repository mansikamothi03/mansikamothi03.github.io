"""
report.py
---------
Generate a ranked theme report from classified + sentiment-scored feedback.
Exports to CSV and prints a console summary ready for Power BI or Tableau.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from typing import Optional


def build_theme_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate feedback into a ranked theme report with:
    - Volume and percentage
    - Average sentiment score
    - % negative / positive
    - Top 3 representative quotes
    """
    report_rows = []

    for theme, group in df.groupby("theme"):
        top_quotes = (
            group.sort_values("theme_confidence", ascending=False)["feedback_text"]
            .head(3)
            .tolist()
        )
        report_rows.append({
            "theme": theme,
            "count": len(group),
            "pct_of_total": round(len(group) / len(df) * 100, 1),
            "avg_sentiment_score": round(group["vader_compound"].mean(), 3),
            "pct_negative": round((group["final_sentiment"] == "negative").mean() * 100, 1),
            "pct_positive": round((group["final_sentiment"] == "positive").mean() * 100, 1),
            "avg_classification_confidence": round(group["theme_confidence"].mean(), 3),
            "top_quote_1": top_quotes[0] if len(top_quotes) > 0 else "",
            "top_quote_2": top_quotes[1] if len(top_quotes) > 1 else "",
            "top_quote_3": top_quotes[2] if len(top_quotes) > 2 else "",
        })

    report = pd.DataFrame(report_rows).sort_values("count", ascending=False).reset_index(drop=True)
    return report


def export_report(
    df: pd.DataFrame,
    report: pd.DataFrame,
    output_dir: str = "data/processed",
) -> None:
    """Export full classified dataset and theme report to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    full_path = os.path.join(output_dir, f"classified_feedback_{timestamp}.csv")
    report_path = os.path.join(output_dir, f"theme_report_{timestamp}.csv")

    # Drop embedding column (not CSV-friendly)
    export_df = df.drop(columns=["embedding", "theme_scores"], errors="ignore")
    export_df.to_csv(full_path, index=False)
    report.to_csv(report_path, index=False)

    print(f"Full dataset exported: {full_path}")
    print(f"Theme report exported: {report_path}")


def plot_theme_volume(
    report: pd.DataFrame,
    save_path: Optional[str] = None,
) -> None:
    """Horizontal bar chart of feedback volume by theme."""
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.tab10.colors

    bars = ax.barh(
        report["theme"],
        report["count"],
        color=[colors[i % 10] for i in range(len(report))],
        alpha=0.85,
    )

    for bar, pct in zip(bars, report["pct_of_total"]):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{pct}%",
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Number of Feedback Records")
    ax.set_title("Feedback Volume by Theme")
    ax.invert_yaxis()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Volume chart saved: {save_path}")
    else:
        plt.show()


def plot_sentiment_heatmap(
    report: pd.DataFrame,
    save_path: Optional[str] = None,
) -> None:
    """Heatmap of sentiment breakdown (positive/neutral/negative) by theme."""
    heat_data = report.set_index("theme")[["pct_positive", "pct_negative"]].copy()
    heat_data["pct_neutral"] = 100 - heat_data["pct_positive"] - heat_data["pct_negative"]
    heat_data = heat_data[["pct_positive", "pct_neutral", "pct_negative"]]
    heat_data.columns = ["Positive %", "Neutral %", "Negative %"]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        heat_data,
        annot=True,
        fmt=".1f",
        cmap="RdYlGn",
        linewidths=0.5,
        ax=ax,
        vmin=0,
        vmax=100,
    )
    ax.set_title("Sentiment Breakdown by Theme (%)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Sentiment heatmap saved: {save_path}")
    else:
        plt.show()


def print_console_summary(report: pd.DataFrame) -> None:
    """Print a clean console summary of the theme report."""
    print("\n" + "=" * 60)
    print("  CUSTOMER FEEDBACK THEME REPORT")
    print("=" * 60)
    for _, row in report.iterrows():
        sentiment_bar = "▓" * int(row["pct_negative"] / 10) + "░" * (10 - int(row["pct_negative"] / 10))
        print(f"\n📌 {row['theme']} ({row['count']} records, {row['pct_of_total']}%)")
        print(f"   Avg sentiment: {row['avg_sentiment_score']:+.3f}  |  Negative: {row['pct_negative']}%  [{sentiment_bar}]")
        print(f"   Top quote: \"{row['top_quote_1'][:80]}...\"")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Demo with synthetic data
    import numpy as np

    np.random.seed(42)
    themes = ["Feature Request", "Billing & Pricing", "Bug Report", "Onboarding", "Performance", "Praise"]
    n = 200

    df = pd.DataFrame({
        "feedback_text": [f"Sample feedback #{i}" for i in range(n)],
        "theme": np.random.choice(themes, n, p=[0.34, 0.25, 0.19, 0.10, 0.07, 0.05]),
        "theme_confidence": np.random.uniform(0.3, 0.95, n),
        "vader_compound": np.random.uniform(-1, 1, n),
        "final_sentiment": np.random.choice(["positive", "neutral", "negative"], n, p=[0.3, 0.4, 0.3]),
    })

    report = build_theme_report(df)
    print_console_summary(report)
    export_report(df, report, output_dir="data/processed")