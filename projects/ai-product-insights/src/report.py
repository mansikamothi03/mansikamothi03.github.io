"""
report.py
---------
Jinja2-based report templating.
Renders the executive brief + metrics into a formatted Markdown or HTML report
ready to share with stakeholders or paste into Notion/Confluence.
"""

import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any


REPORT_TEMPLATE = """# 📊 Weekly Product Insight Brief
**Generated:** {{ generated_at }}  
**Period:** Last 30 days  
**Prepared by:** AI-Assisted Product Insights Tool

---

## Engagement Snapshot

| Metric | Value |
|--------|-------|
| DAU | {{ metrics.dau_wau_mau.dau | format_number }} |
| WAU | {{ metrics.dau_wau_mau.wau | format_number }} |
| MAU | {{ metrics.dau_wau_mau.mau | format_number }} |
| DAU/MAU Stickiness | {{ metrics.dau_wau_mau.dau_mau_ratio }}% |

---

## Executive Brief

{{ brief }}

---

## Feature Adoption (Top 8)

| Feature | Unique Users | Adoption Rate |
|---------|-------------|---------------|
{% for f in metrics.feature_adoption[:8] -%}
| {{ f.feature }} | {{ f.unique_users | format_number }} | {{ f.adoption_rate_pct }}% |
{% endfor %}

---

## Trial-to-Paid Funnel

| Step | Users | Drop-off | Conversion from Top |
|------|-------|----------|---------------------|
{% for s in metrics.funnel -%}
| {{ s.step }} | {{ s.users | format_number }} | {{ s.drop_off_pct if s.drop_off_pct else '—' }}% | {{ s.conversion_from_top_pct }}% |
{% endfor %}

---

## Top 10 Events

| Event | Count | Unique Users |
|-------|-------|-------------|
{% for e in metrics.top_events[:10] -%}
| {{ e.event_type }} | {{ e.event_count | format_number }} | {{ e.unique_users | format_number }} |
{% endfor %}

---

*This report was generated automatically using the AI-Assisted Product Insights Tool.*  
*Source: Amplitude event export · OpenAI GPT-4o · Python*
"""


def format_number(value) -> str:
    """Jinja2 filter: format integers with comma separators."""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


def render_report(
    metrics: Dict[str, Any],
    brief: str,
    output_path: str = "outputs/weekly_brief.md",
) -> str:
    """
    Render the full report as Markdown and save to output_path.

    Args:
        metrics: Output from analyze.aggregate_all()
        brief: Executive brief string from summarize.generate_insight_brief()
        output_path: Where to save the rendered report

    Returns:
        Rendered report as a string
    """
    env = Environment(autoescape=False)
    env.filters["format_number"] = format_number

    template = env.from_string(REPORT_TEMPLATE)
    rendered = template.render(
        metrics=metrics,
        brief=brief,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Report saved: {output_path}")
    return rendered


def render_html_report(
    metrics: Dict[str, Any],
    brief: str,
    output_path: str = "outputs/weekly_brief.html",
) -> str:
    """
    Render the report as HTML (wraps Markdown in a styled HTML shell).
    Useful for email distribution.
    """
    import re

    md_report = render_report(metrics, brief, output_path=output_path.replace(".html", ".md"))

    # Simple Markdown → HTML conversion for headers, bold, tables
    html_body = md_report
    html_body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_body)
    html_body = html_body.replace("\n", "<br>\n")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Weekly Product Insight Brief</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 800px; margin: 40px auto; padding: 0 20px; color: #1a1a2e; }}
  h1 {{ color: #6d28d9; }} h2 {{ color: #4c1d95; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th {{ background: #f3f4f6; padding: 8px 12px; text-align: left; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #e5e7eb; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML report saved: {output_path}")
    return html


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.analyze import aggregate_all
    from src.summarize import generate_insight_brief

    metrics = aggregate_all()
    brief = generate_insight_brief(metrics)
    render_report(metrics, brief)
    render_html_report(metrics, brief)
    print("✅ Reports generated in outputs/")