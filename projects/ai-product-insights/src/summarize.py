"""
summarize.py
------------
OpenAI GPT-4o summarization pipeline.
Takes structured product metrics and generates an executive-ready
insight brief with key findings, risks, and recommended actions.
"""

import os
import json
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a senior product analyst writing a weekly executive brief.
Your audience is the VP of Product and CEO — they are data-literate but time-constrained.
Write in clear, direct prose. No fluff. Lead with the most important insight.
Use specific numbers from the data. Flag risks clearly. End with 3 concrete recommended actions."""

INSIGHT_TEMPLATE = """
Here are this week's product metrics. Generate an executive insight brief.

## Engagement Metrics
- DAU: {dau} | WAU: {wau} | MAU: {mau}
- DAU/MAU stickiness: {dau_mau_ratio}%
- As of: {as_of_date}

## Feature Adoption (Last 30 Days)
{feature_adoption_table}

## Trial-to-Paid Funnel (Last 30 Days)
{funnel_table}

## Top Product Events (Last 30 Days)
{top_events_table}

## Additional Context
{additional_context}

---
Generate a structured executive brief with these sections:
1. **This Week's Headline** (1 sentence, most important finding)
2. **Key Metrics Summary** (3-4 bullet points with specific numbers)
3. **What's Working** (2-3 findings with data)
4. **Risks & Watch Items** (2-3 risks with data)
5. **Recommended Actions** (exactly 3 actions, each with owner and timeline)
"""


def format_table(records: list, columns: list = None) -> str:
    """Format a list of dicts as a simple markdown table."""
    if not records:
        return "No data available."
    import pandas as pd
    df = pd.DataFrame(records)
    if columns:
        df = df[columns]
    return df.to_markdown(index=False)


def generate_insight_brief(
    metrics: Dict[str, Any],
    additional_context: str = "",
    model: str = "gpt-4o",
    temperature: float = 0.3,
) -> str:
    """
    Generate an executive insight brief from structured product metrics.

    Args:
        metrics: Output from analyze.aggregate_all()
        additional_context: Any additional qualitative context to include
        model: OpenAI model to use
        temperature: Lower = more consistent, higher = more creative

    Returns:
        Formatted executive brief as a string
    """
    dau_wau_mau = metrics.get("dau_wau_mau", {})
    feature_adoption = metrics.get("feature_adoption", [])
    funnel = metrics.get("funnel", [])
    top_events = metrics.get("top_events", [])

    feature_table = format_table(
        feature_adoption[:8],  # Top 8 features
        columns=["feature", "unique_users", "adoption_rate_pct"]
    )
    funnel_table = format_table(
        funnel,
        columns=["step", "users", "drop_off_pct", "conversion_from_top_pct"]
    )
    events_table = format_table(
        top_events[:8],
        columns=["event_type", "event_count", "unique_users"]
    )

    prompt = INSIGHT_TEMPLATE.format(
        dau=dau_wau_mau.get("dau", "N/A"),
        wau=dau_wau_mau.get("wau", "N/A"),
        mau=dau_wau_mau.get("mau", "N/A"),
        dau_mau_ratio=dau_wau_mau.get("dau_mau_ratio", "N/A"),
        as_of_date=dau_wau_mau.get("as_of_date", "N/A"),
        feature_adoption_table=feature_table,
        funnel_table=funnel_table,
        top_events_table=events_table,
        additional_context=additional_context or "No additional context provided.",
    )

    print(f"Generating executive brief using {model}...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=1200,
    )

    brief = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    print(f"Brief generated. Tokens used: {tokens_used}")
    return brief


def generate_anomaly_commentary(
    metric_name: str,
    current_value: float,
    prior_value: float,
    context: str = "",
    model: str = "gpt-4o",
) -> str:
    """
    Generate a 2-3 sentence plain-English explanation of a metric anomaly.
    Useful for automated alerting narratives.
    """
    pct_change = ((current_value - prior_value) / prior_value * 100) if prior_value else 0
    direction = "increased" if pct_change > 0 else "decreased"

    prompt = f"""A product metric has changed significantly.

Metric: {metric_name}
Previous value: {prior_value}
Current value: {current_value}
Change: {direction} by {abs(pct_change):.1f}%
Context: {context or 'No additional context.'}

Write 2-3 sentences explaining what this change likely means for the business,
what might have caused it, and what the team should investigate first.
Be specific and actionable. Do not use filler phrases."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.analyze import aggregate_all

    metrics = aggregate_all()
    brief = generate_insight_brief(
        metrics,
        additional_context="Engineering shipped a new onboarding flow last Tuesday. Sales closed 3 enterprise deals this week.",
    )
    print("\n" + "=" * 60)
    print("  EXECUTIVE PRODUCT INSIGHT BRIEF")
    print("=" * 60)
    print(brief)