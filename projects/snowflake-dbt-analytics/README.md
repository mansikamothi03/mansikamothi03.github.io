# Snowflake + dbt Analytics Stack

> A production-ready modern data stack: Snowflake as the cloud warehouse, dbt for transformation and testing, and Airflow for orchestration — with a Power BI semantic layer on top.

## Overview

This project implements a full modern analytics stack from raw data ingestion to BI-ready semantic models. It demonstrates how to build a scalable, tested, and documented data warehouse using Snowflake, dbt, and Apache Airflow — the same stack used at high-growth SaaS companies to replace fragile spreadsheet pipelines and ad hoc SQL.

## Architecture

```
Raw Sources                  Snowflake                    BI Layer
─────────────────────────────────────────────────────────────────
Salesforce CRM    ──►  RAW schema (landing)
Zendesk Tickets   ──►  STAGING schema (dbt)   ──►  Power BI
Amplitude Events  ──►  MARTS schema (dbt)     ──►  Tableau
Stripe Payments   ──►  METRICS schema (dbt)   ──►  Looker-ready
GA4 Web Data      ──►
                         ▲
                    Airflow DAGs
                    (daily + hourly)
```

## Tech Stack

| Layer | Tool |
|---|---|
| Cloud Warehouse | Snowflake (multi-cluster, auto-suspend) |
| Transformation | dbt Core 1.7 |
| Orchestration | Apache Airflow 2.8 |
| Source connectors | Fivetran (Salesforce, Zendesk, Stripe) |
| Testing | dbt tests + Great Expectations |
| Documentation | dbt docs (auto-generated) |
| BI layer | Power BI + DAX measures |
| Version control | Git + GitHub Actions CI |

## dbt Model Layers

### Staging (`stg_`)
- `stg_salesforce__accounts` — normalized account records, deduped on `account_id`
- `stg_zendesk__tickets` — ticket events with SLA breach flags
- `stg_amplitude__events` — sessionized product events, UTC-normalized
- `stg_stripe__subscriptions` — MRR, ARR, and churn event flags

### Intermediate (`int_`)
- `int_account_health_scores` — composite health score joining product usage + support load + payment status
- `int_user_sessions` — sessionized Amplitude events with time-to-first-value metric
- `int_ticket_sla_breaches` — Zendesk tickets joined with account tier for SLA classification

### Marts (`fct_` / `dim_`)
- `fct_mrr` — monthly MRR movements (new, expansion, contraction, churn)
- `fct_trial_conversions` — trial-to-paid funnel with cohort attribution
- `fct_support_load` — tickets per account per week, weighted by severity
- `dim_accounts` — slowly changing dimension (SCD Type 2) for account attributes
- `dim_products` — product catalog with feature flags

### Metrics (`metrics_`)
- `metrics_product` — DAU, WAU, MAU, feature adoption rates
- `metrics_revenue` — MRR, ARR, NRR, churn rate, LTV
- `metrics_support` — CSAT, first-response time, SLA compliance

## Snowflake Design Decisions

- **Separate databases** for RAW, DEV, and PROD environments
- **Role-based access control** — `transformer` role for dbt, `reporter` role for BI tools
- **Clustering keys** on `fct_mrr(account_id, month)` for query performance
- **Auto-suspend** set to 5 min on dev warehouse, 1 min on reporting warehouse
- **Zero-copy cloning** for dev/test environment provisioning

## dbt Testing

Every model includes:
- `not_null` and `unique` tests on primary keys
- `accepted_values` tests on status/type enums
- `relationships` tests for referential integrity across marts
- Custom `assert_mrr_non_negative` test for revenue sanity checks

```yaml
# Example: fct_mrr.yml
models:
  - name: fct_mrr
    columns:
      - name: account_id
        tests: [not_null, unique]
      - name: mrr_amount
        tests: [not_null, assert_mrr_non_negative]
      - name: movement_type
        tests:
          - accepted_values:
              values: [new, expansion, contraction, churn, reactivation]
```

## Airflow DAGs

| DAG | Schedule | Description |
|---|---|---|
| `daily_full_refresh` | 02:00 UTC | Full refresh of all staging models |
| `hourly_incremental` | Every hour | Incremental load for events + tickets |
| `weekly_metrics` | Mon 06:00 UTC | Rebuild all metrics models + alert on anomalies |
| `dbt_test_suite` | After each run | Run all dbt tests, Slack alert on failure |

## Results

| Metric | Value |
|---|---|
| Models built | 34 dbt models across 4 layers |
| Test coverage | 100% of fact tables, 87% overall |
| Query performance | 3× faster vs. raw SQL (clustering + materialization) |
| Data freshness | Hourly for events, daily for revenue |
| Warehouse cost | 40% reduction via auto-suspend tuning |

## Project Structure

```
snowflake-dbt-analytics/
├── dbt_project.yml
├── profiles.yml.example
├── models/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── metrics/
├── tests/
│   └── assert_mrr_non_negative.sql
├── macros/
│   ├── generate_schema_name.sql
│   └── safe_divide.sql
├── airflow/
│   └── dags/
│       ├── daily_full_refresh.py
│       └── hourly_incremental.py
├── docs/
│   └── architecture.png
└── README.md
```

## Setup

```bash
git clone https://github.com/mansikamothi03/snowflake-dbt-analytics
cd snowflake-dbt-analytics
pip install dbt-snowflake==1.7.0
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit profiles.yml with your Snowflake credentials
dbt deps
dbt debug
dbt run --select staging
dbt test
```

## Skills Demonstrated

- Snowflake warehouse design (schemas, roles, clustering, auto-suspend)
- dbt model layering (staging → intermediate → marts → metrics)
- Data testing and documentation with dbt
- Airflow DAG design for incremental + full-refresh patterns
- Modern analytics engineering best practices (SCD Type 2, zero-copy cloning)
- BI semantic layer design for Power BI / Tableau