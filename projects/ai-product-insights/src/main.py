"""
main.py
-------
End-to-end runner for the AI-Assisted Product Insights Tool.

Usage:
    python src/main.py
    python src/main.py --input data/sample_events.csv --context "Engineering shipped new onboarding flow last Tuesday."
    python src/main.py --no-html
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyze import aggregate_all
from src.summarize import generate_insight_brief
from src.report import render_report, render_html_report


def run(
    input_path: str = "data/sample_events.csv",
    context: str = "",
    output_dir: str = "outputs",
    generate_html: bool = True,
    model: str = "gpt-4o",
) -> None:
    print("\n" + "=" * 60)
    print("  AI-ASSISTED PRODUCT INSIGHTS TOOL")
    print("=" * 60)

    # Step 1: Aggregate metrics
    print("\n[1/3] Aggregating product metrics...")
    metrics = aggregate_all(path=input_path)

    dau_wau_mau = metrics["dau_wau_mau"]
    print(f"  DAU: {dau_wau_mau['dau']:,} | WAU: {dau_wau_mau['wau']:,} | MAU: {dau_wau_mau['mau']:,}")
    print(f"  DAU/MAU stickiness: {dau_wau_mau['dau_mau_ratio']}%")
    print(f"  Features tracked: {len(metrics['feature_adoption'])}")
    print(f"  Funnel steps: {len(metrics['funnel'])}")

    # Step 2: Generate AI brief
    print(f"\n[2/3] Generating executive brief with {model}...")
    brief = generate_insight_brief(metrics, additional_context=context, model=model)

    # Step 3: Render reports
    print(f"\n[3/3] Rendering reports to {output_dir}/...")
    os.makedirs(output_dir, exist_ok=True)

    md_path = os.path.join(output_dir, "weekly_brief.md")
    render_report(metrics, brief, output_path=md_path)

    if generate_html:
        html_path = os.path.join(output_dir, "weekly_brief.html")
        render_html_report(metrics, brief, output_path=html_path)

    print("\n" + "=" * 60)
    print("  EXECUTIVE BRIEF PREVIEW")
    print("=" * 60)
    print(brief)
    print("\n✅ Done. Reports saved to", output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Assisted Product Insights Tool")
    parser.add_argument(
        "--input",
        default="data/sample_events.csv",
        help="Path to product events CSV (Amplitude/Mixpanel/GA4 export format)",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Additional qualitative context for the AI brief (e.g. recent launches, incidents)",
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Output directory for reports",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML report generation",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        help="OpenAI model to use for brief generation",
    )

    args = parser.parse_args()
    run(
        input_path=args.input,
        context=args.context,
        output_dir=args.output,
        generate_html=not args.no_html,
        model=args.model,
    )