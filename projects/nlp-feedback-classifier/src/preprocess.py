"""
preprocess.py
-------------
Text cleaning and normalization pipeline for customer feedback.
"""

import re
import string
import pandas as pd
import spacy
from typing import List

# Load spaCy English model (run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None


def clean_text(text: str) -> str:
    """Remove URLs, HTML tags, special characters, and normalize whitespace."""
    if not isinstance(text, str):
        return ""
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)
    # Remove punctuation except apostrophes
    text = text.translate(str.maketrans("", "", string.punctuation.replace("'", "")))
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def lemmatize(text: str) -> str:
    """Lemmatize text using spaCy, removing stopwords and short tokens."""
    if nlp is None or not text:
        return text
    doc = nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and len(token.text) > 2
    ]
    return " ".join(tokens)


def deduplicate(df: pd.DataFrame, text_col: str = "feedback_text") -> pd.DataFrame:
    """Remove exact duplicate feedback entries."""
    before = len(df)
    df = df.drop_duplicates(subset=[text_col]).reset_index(drop=True)
    after = len(df)
    print(f"Deduplication: {before} → {after} rows ({before - after} removed)")
    return df


def preprocess_dataframe(
    df: pd.DataFrame,
    text_col: str = "feedback_text",
    lemmatize_text: bool = True,
) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. Drop nulls
    2. Clean text
    3. Deduplicate
    4. Lemmatize (optional)
    """
    df = df.dropna(subset=[text_col]).copy()
    df["cleaned_text"] = df[text_col].apply(clean_text)
    df = deduplicate(df, text_col="cleaned_text")
    df = df[df["cleaned_text"].str.len() > 10].reset_index(drop=True)

    if lemmatize_text:
        print("Lemmatizing... (this may take a moment)")
        df["lemmatized_text"] = df["cleaned_text"].apply(lemmatize)
    else:
        df["lemmatized_text"] = df["cleaned_text"]

    print(f"Preprocessing complete: {len(df)} records ready.")
    return df


if __name__ == "__main__":
    # Quick smoke test
    sample = pd.DataFrame({
        "feedback_text": [
            "The billing page is so confusing! I can't find my invoices.",
            "Love the new dashboard feature, very intuitive.",
            "SSO login keeps failing every morning. Very frustrating.",
            "The billing page is so confusing! I can't find my invoices.",  # duplicate
            None,
        ]
    })
    result = preprocess_dataframe(sample)
    print(result[["feedback_text", "cleaned_text", "lemmatized_text"]])