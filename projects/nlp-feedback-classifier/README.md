# NLP Customer Feedback Classifier

> Classify, cluster, and surface themes from raw customer feedback at scale using spaCy, OpenAI embeddings, and scikit-learn.

## Overview

Customer feedback arrives from multiple channels — NPS surveys, G2/Capterra reviews, Zendesk tickets, and in-app prompts — but most teams read it manually or ignore it entirely. This project builds an end-to-end NLP pipeline that ingests raw text feedback, classifies it by sentiment and product theme, clusters similar responses, and outputs a ranked theme dashboard so product teams can act on signal instead of noise.

## Problem

- 500–2,000 feedback responses per month across 4 channels
- No consistent taxonomy — every analyst tagged themes differently
- Leadership asked "what are customers saying?" but answers took 2–3 days of manual reading
- High-signal churn warnings buried in low-priority ticket queues

## Solution

A three-stage NLP pipeline:

1. **Preprocessing** — clean, deduplicate, and normalize text (spaCy tokenization, stopword removal, lemmatization)
2. **Classification** — fine-tuned zero-shot classifier (OpenAI `text-embedding-3-small`) assigns each response to a product theme taxonomy (Onboarding, Billing, Performance, Feature Request, Bug, Praise)
3. **Clustering** — K-Means on embeddings groups semantically similar responses; silhouette scoring selects optimal K
4. **Sentiment scoring** — VADER + GPT-4o for nuanced sentiment on short vs. long-form text
5. **Dashboard output** — ranked theme table with volume, avg sentiment, and representative quotes exported to CSV / Power BI

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| NLP | spaCy, NLTK, VADER |
| Embeddings | OpenAI `text-embedding-3-small` |
| Classification | scikit-learn (zero-shot + logistic regression) |
| Clustering | scikit-learn KMeans, silhouette analysis |
| LLM summarization | OpenAI GPT-4o |
| Data | pandas, numpy |
| Visualization | matplotlib, seaborn, Power BI export |

## Results

| Metric | Value |
|---|---|
| Classification accuracy | 91.4% (vs. human labels) |
| Themes identified | 6 primary, 14 sub-themes |
| Processing time | ~800 responses in < 2 min |
| Manual review time saved | ~12 hrs/week |
| Churn-signal tickets surfaced | 23% faster than manual triage |

## Key Findings (sample run)

- **Top theme by volume:** Feature Requests (34%) — primarily around bulk export and API access
- **Highest negative sentiment:** Billing & Pricing (avg score: −0.62)
- **Fastest-growing complaint cluster:** SSO / authentication issues (+180% MoM)
- **Hidden churn signal:** "cancellation" keyword co-occurred with "slow" and "support" in 78% of at-risk accounts

## Project Structure

```
nlp-feedback-classifier/
├── data/
│   ├── raw/                  # Raw feedback CSVs (gitignored)
│   └── processed/            # Cleaned + labeled outputs
├── notebooks/
│   ├── 01_eda.ipynb          # Exploratory analysis
│   ├── 02_classification.ipynb
│   └── 03_clustering.ipynb
├── src/
│   ├── preprocess.py         # Text cleaning pipeline
│   ├── embed.py              # OpenAI embedding calls
│   ├── classify.py           # Theme classification
│   ├── cluster.py            # KMeans + silhouette
│   ├── sentiment.py          # VADER + GPT-4o scoring
│   └── report.py             # Dashboard export
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/mansikamothi03/nlp-feedback-classifier
cd nlp-feedback-classifier
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
python src/classify.py --input data/raw/feedback.csv --output data/processed/
```

## Skills Demonstrated

- End-to-end NLP pipeline design
- OpenAI embeddings + GPT-4o for classification and summarization
- Unsupervised clustering with silhouette-based model selection
- Translating unstructured text into actionable product insights
- Connecting feedback themes to churn and retention signals