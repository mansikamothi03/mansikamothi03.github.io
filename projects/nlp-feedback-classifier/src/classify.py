"""
classify.py
-----------
Zero-shot theme classification using OpenAI embeddings + cosine similarity.
Assigns each feedback record to one of the predefined product theme categories.
"""

import os
import numpy as np
import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Canonical product theme taxonomy
THEMES = {
    "Feature Request": [
        "I wish the product had",
        "please add the ability to",
        "it would be great if you could add",
        "missing feature",
        "feature request",
        "would love to see",
    ],
    "Billing & Pricing": [
        "billing issue",
        "invoice problem",
        "charge on my account",
        "pricing is too high",
        "unexpected charge",
        "subscription cost",
        "refund request",
    ],
    "Bug Report": [
        "this is broken",
        "error message",
        "not working",
        "crashes",
        "bug in the software",
        "unexpected behavior",
        "glitch",
    ],
    "Onboarding": [
        "hard to get started",
        "confusing setup",
        "onboarding is unclear",
        "documentation is lacking",
        "first time using",
        "tutorial needed",
    ],
    "Performance": [
        "the app is slow",
        "loading takes too long",
        "timeout error",
        "laggy interface",
        "performance issue",
        "response time is bad",
    ],
    "Praise": [
        "love this product",
        "great experience",
        "excellent support",
        "highly recommend",
        "fantastic tool",
        "works perfectly",
    ],
}


def _get_theme_embeddings(model: str = "text-embedding-3-small") -> Dict[str, np.ndarray]:
    """Embed each theme's representative phrases and average them."""
    theme_embeddings = {}
    for theme, phrases in THEMES.items():
        responses = client.embeddings.create(input=phrases, model=model)
        phrase_embeddings = np.array([r.embedding for r in responses.data])
        theme_embeddings[theme] = phrase_embeddings.mean(axis=0)
    return theme_embeddings


def classify_themes(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    model: str = "text-embedding-3-small",
    confidence_threshold: float = 0.25,
) -> pd.DataFrame:
    """
    Assign each feedback record a theme and confidence score
    using cosine similarity between feedback embeddings and theme centroids.
    """
    print("Computing theme centroids...")
    theme_embeddings = _get_theme_embeddings(model=model)

    theme_names = list(theme_embeddings.keys())
    theme_matrix = np.array([theme_embeddings[t] for t in theme_names])

    print(f"Classifying {len(embeddings)} records into {len(theme_names)} themes...")
    similarities = cosine_similarity(embeddings, theme_matrix)

    df = df.copy()
    df["theme"] = [theme_names[i] for i in similarities.argmax(axis=1)]
    df["theme_confidence"] = similarities.max(axis=1)
    df["theme_scores"] = [
        dict(zip(theme_names, row.tolist())) for row in similarities
    ]

    # Flag low-confidence classifications
    df["theme_uncertain"] = df["theme_confidence"] < confidence_threshold

    uncertain_count = df["theme_uncertain"].sum()
    print(f"Classification complete. {uncertain_count} records flagged as uncertain (confidence < {confidence_threshold}).")

    return df


def print_theme_distribution(df: pd.DataFrame) -> None:
    """Print a summary of theme distribution."""
    dist = (
        df.groupby("theme")
        .agg(count=("theme", "count"), avg_confidence=("theme_confidence", "mean"))
        .sort_values("count", ascending=False)
    )
    dist["pct"] = (dist["count"] / dist["count"].sum() * 100).round(1)
    print("\n=== Theme Distribution ===")
    print(dist.to_string())


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.preprocess import preprocess_dataframe
    from src.embed import embed_dataframe

    sample = pd.DataFrame({
        "feedback_text": [
            "The billing page is so confusing, I can't find my invoices.",
            "SSO login keeps failing every morning. Very frustrating.",
            "Love the new dashboard feature, very intuitive.",
            "Please add bulk CSV export — we need it badly.",
            "The app crashes whenever I try to upload a file larger than 10MB.",
            "Getting started was really hard, the docs are outdated.",
        ]
    })

    df = preprocess_dataframe(sample, lemmatize_text=False)
    df, embeddings = embed_dataframe(df, text_col="cleaned_text")
    df = classify_themes(df, embeddings)
    print_theme_distribution(df)
    print(df[["feedback_text", "theme", "theme_confidence"]].to_string())