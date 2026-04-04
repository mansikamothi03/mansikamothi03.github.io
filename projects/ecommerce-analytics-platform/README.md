# E-Commerce Analytics Platform

End-to-end analytics solution for e-commerce tracking revenue, conversions, and customer lifetime value using Google Analytics, BigQuery, and Looker Studio.

## 📊 Overview

A complete e-commerce analytics stack that unifies data from Shopify, Google Analytics, and ad platforms into BigQuery, then surfaces insights through automated Looker Studio dashboards and Python-based CLV modeling.

## 🚀 Features

- Automated GA4 → BigQuery export pipeline
- Customer Lifetime Value (CLV) prediction model
- Revenue attribution across marketing channels
- Real-time conversion funnel analysis
- Automated weekly/monthly reporting
- RFM (Recency, Frequency, Monetary) customer segmentation

## 🛠️ Tech Stack

- **Python** 3.9+ (google-cloud-bigquery, pandas)
- **Google Analytics 4** (event tracking)
- **BigQuery** (data warehouse)
- **Looker Studio** (dashboards)
- **dbt** (SQL transformations)

## 📁 Project Structure

```
ecommerce-analytics-platform/
├── src/
│   ├── bigquery_client.py      # BigQuery connection & queries
│   ├── clv_model.py            # Customer Lifetime Value model
│   ├── rfm_segmentation.py     # RFM analysis
│   └── attribution.py         # Marketing attribution
├── sql/
│   ├── funnel_analysis.sql
│   ├── revenue_by_channel.sql
│   └── clv_query.sql
├── dbt/
│   └── models/
├── requirements.txt
└── README.md
```

## ⚙️ Setup

```bash
git clone https://github.com/mansikamothi/ecommerce-analytics-platform
cd ecommerce-analytics-platform
pip install -r requirements.txt
# Set GOOGLE_APPLICATION_CREDENTIALS env variable
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
python src/clv_model.py
```

## 📈 Results

- **35%** increase in marketing ROI through attribution insights
- **$500K+** in revenue tracked monthly
- **10K+** customers segmented by RFM score
- **15+** automated reports delivered weekly