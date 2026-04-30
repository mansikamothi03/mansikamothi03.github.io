"""
sentiment.py
------------
Dual-layer sentiment scoring:
1. VADER — fast rule-based sentiment for short text
2. GPT-4o — nuanced sentiment for longer or ambiguous feedback
"""

import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vader = SentimentIntensityAnalyzer()

SentimentLabel = Literal["positive", "neutral", "negative"]


def vader_sentiment(text: str) -> dict:
    """
    Score sentiment using VADER.
    Returns compound score (-1 to 1) and label.
    """
    scores = vader.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {"vader_compound": compound, "vader_label": label}


def gpt_sentiment(text: str, model: str = "gpt-4o") -> dict:
    """
    Score sentiment using GPT-4o for nuanced or long-form feedback.
    Returns label and a brief rationale.
    """
    prompt = f"""Analyze the sentiment of the following customer feedback.
Respond with a JSON object with two keys:
- "label": one of "positive", "neutral", or "negative"
- "rationale": one sentence explaining why

Feedback: "{text}"

Respond with valid JSON only."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return {
        "gpt_label": result.get("label", "neutral"),
        "gpt_rationale": result.get("rationale", ""),
    }


def score_sentiment(
    df: pd.DataFrame,
    text_col: str = "cleaned_text",
    use_gpt: bool = False,
    gpt_threshold_words: int = 20,
) -> pd.DataFrame:
    """
    Apply sentiment scoring to a dataframe.
    - Always applies VADER.
    - Applies GPT-4o only if use_gpt=True AND text is longer than gpt_threshold_words.
    """
    df = df.copy()

    print("Applying VADER sentiment scoring...")
    vader_results = df[text_col].apply(vader_sentiment)
    df["vader_compound"] = vader_results.apply(lambda x: x["vader_compound"])
    df["vader_label"] = vader_results.apply(lambda x: x["vader_label"])

    if use_gpt:
        print("Applying GPT-4o sentiment for long/ambiguous feedback...")
        long_mask = df[text_col].str.split().str.len() >= gpt_threshold_words
        gpt_results = []

        for idx, row in df.iterrows():
            if long_mask[idx]:
                result = gpt_sentiment(row[text_col])
            else:
                result = {"gpt_label": row["vader_label"], "gpt_rationale": "VADER (short text)"}
            gpt_results.append(result)

        df["gpt_label"] = [r["gpt_label"] for r in gpt_results]
        df["gpt_rationale"] = [r["gpt_rationale"] for r in gpt_results]
        df["final_sentiment"] = df["gpt_label"]
    else:
        df["final_sentiment"] = df["vader_label"]

    # Summary
    dist = df["final_sentiment"].value_counts()
    print(f"\nSentiment distribution:\n{dist.to_string()}")

    return df


def sentiment_by_theme(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate average sentiment score by theme."""
    return (
        df.groupby("theme")
        .agg(
            count=("theme", "count"),
            avg_vader_score=("vader_compound", "mean"),
            pct_negative=("final_sentiment", lambda x: (x == "negative").mean() * 100),
            pct_positive=("final_sentiment", lambda x: (x == "positive").mean() * 100),
        )
        .round(3)
        .sort_values("avg_vader_score")
    )


if __name__ == "__main__":
    sample = pd.DataFrame({
        "cleaned_text": [
            "the billing page is so confusing i cannot find my invoices",
            "love the new dashboard feature very intuitive",
            "sso login keeps failing every morning very frustrating",
            "please add bulk csv export we need it badly for our workflow",
            "the app crashes whenever i try to upload a file larger than 10mb this is unacceptable",
        ],
        "theme": ["Billing & Pricing", "Praise", "Bug Report", "Feature Request", "Bug Report"],
    })

    result = score_sentiment(sample, text_col="cleaned_text", use_gpt=False)
    print(result[["cleaned_text", "vader_compound", "vader_label", "final_sentiment"]])
    print("\nBy theme:")
    print(sentiment_by_theme(result))