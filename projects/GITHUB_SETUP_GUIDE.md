# 🚀 GitHub Setup Guide — Push All 6 Projects

Follow these steps to push each project to GitHub and link them to your portfolio.

---

## Prerequisites

```bash
git config --global user.name "Mansi Kamothi"
git config --global user.email "mansikamothi1999@gmail.com"
```

---

## Project 1: Customer Analytics Dashboard

```bash
cd portfolio/projects/customer-analytics-dashboard
git init
git add .
git commit -m "Initial commit: Customer Analytics Dashboard with churn prediction and cohort analysis"
git branch -M main
git remote add origin https://github.com/mansikamothi/customer-analytics-dashboard.git
git push -u origin main
```

**GitHub repo name:** `customer-analytics-dashboard`

---

## Project 2: Product Feature Optimization (A/B Testing)

```bash
cd portfolio/projects/product-feature-optimization
git init
git add .
git commit -m "Initial commit: A/B testing framework with statistical significance testing"
git branch -M main
git remote add origin https://github.com/mansikamothi/product-feature-optimization.git
git push -u origin main
```

**GitHub repo name:** `product-feature-optimization`

---

## Project 3: Data Pipeline Automation

```bash
cd portfolio/projects/data-pipeline-automation
git init
git add .
git commit -m "Initial commit: Apache Airflow ETL pipeline with data quality validation"
git branch -M main
git remote add origin https://github.com/mansikamothi/data-pipeline-automation.git
git push -u origin main
```

**GitHub repo name:** `data-pipeline-automation`

---

## Project 4: E-Commerce Analytics Platform

```bash
cd portfolio/projects/ecommerce-analytics-platform
git init
git add .
git commit -m "Initial commit: CLV prediction model and RFM segmentation for e-commerce"
git branch -M main
git remote add origin https://github.com/mansikamothi/ecommerce-analytics-platform.git
git push -u origin main
```

**GitHub repo name:** `ecommerce-analytics-platform`

---

## Project 5: ML Recommendation System

```bash
cd portfolio/projects/ml-recommendation-system
git init
git add .
git commit -m "Initial commit: Hybrid collaborative + content-based recommendation engine"
git branch -M main
git remote add origin https://github.com/mansikamothi/ml-recommendation-system.git
git push -u origin main
```

**GitHub repo name:** `ml-recommendation-system`

---

## Project 6: Real-Time Monitoring Dashboard

```bash
cd portfolio/projects/realtime-monitoring-dashboard
git init
git add .
git commit -m "Initial commit: FastAPI WebSocket backend + React dashboard with anomaly detection"
git branch -M main
git remote add origin https://github.com/mansikamothi/realtime-monitoring-dashboard.git
git push -u origin main
```

**GitHub repo name:** `realtime-monitoring-dashboard`

---

## After Pushing — Update Portfolio Links

Once repos are live, update `portfolio/index.html` to add GitHub links to each project card.
Replace each `View Details` button with both a GitHub link and a details button.

The GitHub URLs will be:
- `https://github.com/mansikamothi/customer-analytics-dashboard`
- `https://github.com/mansikamothi/product-feature-optimization`
- `https://github.com/mansikamothi/data-pipeline-automation`
- `https://github.com/mansikamothi/ecommerce-analytics-platform`
- `https://github.com/mansikamothi/ml-recommendation-system`
- `https://github.com/mansikamothi/realtime-monitoring-dashboard`

---

## Create GitHub Repos (Web UI)

1. Go to https://github.com/new
2. Set repo name (e.g. `customer-analytics-dashboard`)
3. Set to **Public**
4. Do NOT initialize with README (you already have one)
5. Click **Create repository**
6. Run the git commands above