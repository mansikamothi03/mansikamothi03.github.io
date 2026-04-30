"""
embed.py
--------
Generate OpenAI text embeddings for feedback records.
Embeddings are used for semantic clustering and zero-shot classification.
"""

import os
import time
import numpy as np
import pandas as pd
from openai import OpenAI
from typing import List
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per request


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> List[float]:
    """Get embedding for a single text string."""
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


def get_embeddings_batch(
    texts: List[str],
    model: str = EMBEDDING_MODEL,
    batch_size: int = BATCH_SIZE,
    sleep_between_batches: float = 0.5,
) -> np.ndarray:
    """
    Get embeddings for a list of texts in batches.
    Returns a 2D numpy array of shape (n_texts, embedding_dim).
    """
    all_embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch = [t.replace("\n", " ") for t in batch]
        batch_num = i // batch_size + 1
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} texts)...")

        response = client.embeddings.create(input=batch, model=model)
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

        if i + batch_size < len(texts):
            time.sleep(sleep_between_batches)

    return np.array(all_embeddings)


def embed_dataframe(
    df: pd.DataFrame,
    text_col: str = "cleaned_text",
    save_path: str = None,
) -> pd.DataFrame:
    """
    Add an 'embedding' column to the dataframe.
    Optionally save embeddings to a .npy file for reuse.
    """
    texts = df[text_col].tolist()
    print(f"Generating embeddings for {len(texts)} texts using {EMBEDDING_MODEL}...")
    embeddings = get_embeddings_batch(texts)

    df = df.copy()
    df["embedding"] = list(embeddings)

    if save_path:
        np.save(save_path, embeddings)
        print(f"Embeddings saved to {save_path}")

    print(f"Done. Embedding shape: {embeddings.shape}")
    return df, embeddings


if __name__ == "__main__":
    # Smoke test with 3 sample texts
    sample_texts = [
        "The billing page is confusing and I cannot find my invoices.",
        "SSO login keeps failing every morning.",
        "Love the new dashboard, very intuitive and fast.",
    ]
    print("Testing single embedding...")
    emb = get_embedding(sample_texts[0])
    print(f"Embedding dimension: {len(emb)}")

    print("\nTesting batch embeddings...")
    embs = get_embeddings_batch(sample_texts, batch_size=3)
    print(f"Batch shape: {embs.shape}")