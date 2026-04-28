# Zendesk Support Analytics Dashboard

A Python + SQL + Tableau project that analyzes Zendesk support ticket data to surface CSAT trends, ticket volume by category, resolution time, and agent performance — enabling product and operations teams to reduce support load and improve customer experience.

## Business Problem

Support teams generate thousands of tickets per month, but the insights are buried in raw data. This project answers:
- Which product areas generate the most tickets?
- What is the average resolution time by category and agent?
- Where are CSAT scores dropping and why?
- Which bug fixes would have the highest ticket-reduction impact?

## Impact (Simulated)

- Identified top 3 ticket categories driving 62% of volume
- Surfaced 3 product bugs whose fixes reduced ticket volume by ~18%
- Reduced average resolution time visibility lag from weekly to real-time

## Tech Stack

- **Python** (pandas, numpy) — data cleaning, aggregation, trend analysis
- **SQL** — ticket segmentation, CSAT joins, agent performance queries
- **Tableau** — operational dashboard (ticket volume, resolution time, CSAT, escalation rate)
- **Mock Data** — generated realistic Zendesk-style ticket dataset

## Project Structure

```
zendesk-support-analytics/
├── data/
│   └── mock_tickets.csv          # Simulated Zendesk ticket export
├── sql/
│   └── ticket_analysis.sql       # Core queries: volume, CSAT, resolution time
├── src/
│   └── analyze_tickets.py        # Python analysis pipeline
├── dashboard/
│   └── zendesk_dashboard.png     # Tableau dashboard screenshot
└── README.md
```

## Key Analyses

### 1. Ticket Volume by Category
```sql
SELECT category, COUNT(*) as ticket_count,
       ROUND(AVG(resolution_hours), 1) as avg_resolution_hrs,
       ROUND(AVG(csat_score), 2) as avg_csat
FROM tickets
WHERE created_date >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)
GROUP BY category
ORDER BY ticket_count DESC;
```

### 2. CSAT Trend Analysis
```python
import pandas as pd

df = pd.read_csv('data/mock_tickets.csv')
df['created_date'] = pd.to_datetime(df['created_date'])
df['week'] = df['created_date'].dt.to_period('W')

csat_trend = df.groupby('week')['csat_score'].mean().reset_index()
print(csat_trend)
```

### 3. Top Bug Fix Opportunities
Tickets tagged as `bug` with high volume + low CSAT = highest ROI for engineering prioritization.

## How to Run

```bash
pip install pandas numpy matplotlib seaborn
python src/analyze_tickets.py
```

## Skills Demonstrated

- Zendesk data modeling and ticket taxonomy
- SQL aggregation and time-series analysis
- Python data pipeline (ETL → analysis → output)
- Operational dashboard design for Support + Product teams
- Translating support data into product prioritization recommendations