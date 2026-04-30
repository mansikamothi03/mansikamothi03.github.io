"""
cluster.py
----------
KMeans clustering on OpenAI embeddings with silhouette-based K selection.
Groups semantically similar feedback responses into clusters.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from typing import Tuple, List


def find_optimal_k(
    embeddings: np.ndarray,
    k_min: int = 3,
    k_max: int = 15,
    random_state: int = 42,
) -> Tuple[int, List[float]]:
    """
    Use silhouette scoring to find the optimal number of clusters K.
    Returns the best K and the list of silhouette scores.
    """
    silhouette_scores = []
    k_range = range(k_min, k_max + 1)

    print(f"Testing K from {k_min} to {k_max}...")
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        silhouette_scores.append(score)
        print(f"  K={k}: silhouette={score:.4f}")

    best_k = k_range[int(np.argmax(silhouette_scores))]
    print(f"\nOptimal K: {best_k} (silhouette={max(silhouette_scores):.4f})")
    return best_k, silhouette_scores


def cluster_embeddings(
    embeddings: np.ndarray,
    k: int,
    random_state: int = 42,
) -> Tuple[np.ndarray, KMeans]:
    """
    Fit KMeans with the given K and return cluster labels + fitted model.
    """
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    score = silhouette_score(embeddings, labels)
    print(f"KMeans fitted: K={k}, silhouette={score:.4f}")
    return labels, kmeans


def get_cluster_representatives(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    kmeans: KMeans,
    text_col: str = "feedback_text",
    n_per_cluster: int = 3,
) -> pd.DataFrame:
    """
    For each cluster, find the N feedback records closest to the centroid.
    Returns a dataframe of representative quotes per cluster.
    """
    from sklearn.metrics.pairwise import cosine_similarity

    representatives = []
    for cluster_id in range(kmeans.n_clusters):
        centroid = kmeans.cluster_centers_[cluster_id].reshape(1, -1)
        cluster_mask = df["cluster"] == cluster_id
        cluster_indices = df[cluster_mask].index.tolist()

        if not cluster_indices:
            continue

        cluster_embeddings = embeddings[cluster_indices]
        sims = cosine_similarity(cluster_embeddings, centroid).flatten()
        top_n = np.argsort(sims)[::-1][:n_per_cluster]

        for rank, idx in enumerate(top_n):
            original_idx = cluster_indices[idx]
            representatives.append({
                "cluster": cluster_id,
                "rank": rank + 1,
                "similarity_to_centroid": sims[idx],
                "feedback_text": df.loc[original_idx, text_col],
            })

    return pd.DataFrame(representatives)


def plot_clusters(
    embeddings: np.ndarray,
    labels: np.ndarray,
    title: str = "Feedback Clusters (PCA 2D)",
    save_path: str = None,
) -> None:
    """Reduce embeddings to 2D with PCA and plot cluster assignments."""
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(embeddings)

    plt.figure(figsize=(10, 7))
    scatter = plt.scatter(
        coords[:, 0], coords[:, 1],
        c=labels, cmap="tab10", alpha=0.7, s=30
    )
    plt.colorbar(scatter, label="Cluster")
    plt.title(title)
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def plot_silhouette_scores(
    k_range: range,
    scores: List[float],
    best_k: int,
    save_path: str = None,
) -> None:
    """Plot silhouette scores across K values."""
    plt.figure(figsize=(8, 4))
    plt.plot(list(k_range), scores, marker="o", color="#a78bfa")
    plt.axvline(x=best_k, color="#34d399", linestyle="--", label=f"Best K={best_k}")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score vs. K")
    plt.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
    else:
        plt.show()


if __name__ == "__main__":
    # Generate synthetic embeddings for testing (no API key needed)
    np.random.seed(42)
    n_samples = 120
    # Simulate 6 natural clusters in 1536-dim space (reduced for speed)
    dim = 64
    centers = np.random.randn(6, dim)
    embeddings = np.vstack([
        centers[i] + np.random.randn(20, dim) * 0.3
        for i in range(6)
    ])

    best_k, scores = find_optimal_k(embeddings, k_min=3, k_max=10)
    labels, kmeans = cluster_embeddings(embeddings, k=best_k)
    print(f"\nCluster label distribution: {dict(zip(*np.unique(labels, return_counts=True)))}")