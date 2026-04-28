# AI-Assisted Product Insights Tool

A Python tool that takes raw product event data, uses the OpenAI API to generate plain-English executive summaries, and outputs a formatted decision-ready report — demonstrating AI-assisted workflow automation for product analytics teams.

## Business Problem

Product analysts spend hours each week writing narrative summaries of dashboard data for leadership. This tool automates that process: feed it raw metrics, get back a structured executive brief in seconds.

## Impact (Simulated)

- Reduced executive report prep time by ~40%
- Standardized insight format across Product, Sales, and Operations
- Enabled non-technical stakeholders to consume product data without analyst bottleneck

## Tech Stack

- **Python** (pandas, openai) — data ingestion + LLM summarization
- **OpenAI API** (GPT-4) — narrative generation from structured metrics
- **Jinja2** — report templating
- **CSV / JSON** — input data format (compatible with Amplitude, Mixpanel, GA4 exports)

## Project Structure

```
ai-product-insights/
├── data/
│   └── sample_events.csv         # Sample product event export
├── src/
│   ├── analyze.py                # Metric aggregation pipeline
│   ├── summarize.py              # OpenAI API summarization
│   └── report.py                 # Report generation
├── templates/
│   └── executive_brief.md        # Output template
├── output/
│   └── sample_report.md          # Example generated report
└── README.md
```

## How It Works

### Step 1 — Aggregate metrics from raw event data
```python
import pandas as pd

df = pd.read_csv('data/sample_events.csv')
df['date'] = pd.to_datetime(df['date'])

summary = {
    'total_events': len(df),
    'dau': df.groupby('date')['user_id'].nunique().mean().round(0),
    'top_features': df['feature'].value_counts().head(3).to_dict(),
    'drop_off_step': df[df['completed'] == False]['step'].value_counts().idxmax(),
    'conversion_rate': round(df['converted'].mean() * 100, 1)
}
```

### Step 2 — Generate executive summary via OpenAI
```python
import openai

def generate_summary(metrics: dict) -> str:
    prompt = f"""
    You are a senior product analyst. Based on the following product metrics,
    write a concise 3-paragraph executive summary with: (1) key findings,
    (2) risks or drop-off points, (3) recommended next actions.

    Metrics:
    {metrics}

    Format: plain English, no jargon, decision-ready.
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Step 3 — Output formatted report
```python
from datetime import date

def save_report(summary: str, metrics: dict):
    with open('output/executive_brief.md', 'w') as f:
        f.write(f"# Product Insights Brief — {date.today()}\n\n")
        f.write(f"**Conversion Rate:** {metrics['conversion_rate']}%\n")
        f.write(f"**DAU (avg):** {metrics['dau']}\n\n")
        f.write(summary)
```

## Sample Output

```
# Product Insights Brief — 2024-11-15

**Conversion Rate:** 23.4%
**DAU (avg):** 1,842

## Key Findings
Trial-to-paid conversion held at 23.4% this week, up 1.2pp from last week.
The onboarding flow drove the highest engagement, with 'dashboard setup'
being the most-used feature among converted users...

## Risks
Step 3 of onboarding ('invite team member') shows a 34% drop-off rate —
the highest in the funnel. Users who skip this step convert at half the rate...

## Recommended Actions
1. A/B test a simplified team invite flow with a skip option
2. Add a progress indicator to the onboarding checklist
3. Trigger a targeted email at step 3 drop-off with a 1-click invite link
```

## How to Run

```bash
pip install pandas openai jinja2
export OPENAI_API_KEY=your_key_here
python src/analyze.py
python src/summarize.py
python src/report.py
```

## Skills Demonstrated

- AI/LLM integration for business workflow automation
- Prompt engineering for structured analytical output
- Python data pipeline (ingest → aggregate → summarize → report)
- Product analytics instrumentation and metric design
- Executive communication and stakeholder reporting