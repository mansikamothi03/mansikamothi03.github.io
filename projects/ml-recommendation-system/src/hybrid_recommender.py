"""
Hybrid Recommendation System
Combines collaborative filtering (SVD) and content-based filtering.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeFilter:
    """SVD-based collaborative filtering."""

    def __init__(self, n_components: int = 50):
        self.n_components = n_components
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_factors = None
        self.item_factors = None
        self.user_index = {}
        self.item_index = {}

    def fit(self, ratings_df: pd.DataFrame):
        """
        Fit SVD on user-item ratings matrix.
        
        Args:
            ratings_df: DataFrame with columns [user_id, item_id, rating]
        """
        self.user_index = {u: i for i, u in enumerate(ratings_df['user_id'].unique())}
        self.item_index = {it: i for i, it in enumerate(ratings_df['item_id'].unique())}

        n_users = len(self.user_index)
        n_items = len(self.item_index)
        matrix = np.zeros((n_users, n_items))

        for _, row in ratings_df.iterrows():
            u = self.user_index[row['user_id']]
            it = self.item_index[row['item_id']]
            matrix[u, it] = row['rating']

        self.user_factors = self.svd.fit_transform(matrix)
        self.item_factors = self.svd.components_.T
        logger.info(f"Collaborative filter fitted: {n_users} users, {n_items} items")

    def recommend(self, user_id: int, n: int = 10, exclude_seen: list = None) -> list:
        """Get top-N recommendations for a user."""
        if user_id not in self.user_index:
            return []

        u_idx = self.user_index[user_id]
        scores = self.user_factors[u_idx] @ self.item_factors.T
        item_ids = list(self.item_index.keys())

        recs = sorted(zip(item_ids, scores), key=lambda x: x[1], reverse=True)
        if exclude_seen:
            recs = [(iid, s) for iid, s in recs if iid not in exclude_seen]

        return recs[:n]


class ContentFilter:
    """Content-based filtering using TF-IDF on item features."""

    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        self.item_matrix = None
        self.item_ids = []

    def fit(self, items_df: pd.DataFrame):
        """
        Fit TF-IDF on item descriptions/tags.
        
        Args:
            items_df: DataFrame with columns [item_id, description, tags, category]
        """
        self.item_ids = items_df['item_id'].tolist()
        text_features = (
            items_df['description'].fillna('') + ' ' +
            items_df['tags'].fillna('') + ' ' +
            items_df['category'].fillna('')
        )
        self.item_matrix = self.tfidf.fit_transform(text_features)
        logger.info(f"Content filter fitted: {len(self.item_ids)} items")

    def similar_items(self, item_id: int, n: int = 10) -> list:
        """Get N most similar items to a given item."""
        if item_id not in self.item_ids:
            return []

        idx = self.item_ids.index(item_id)
        item_vec = self.item_matrix[idx]
        similarities = cosine_similarity(item_vec, self.item_matrix).flatten()
        similar_indices = similarities.argsort()[::-1][1:n+1]

        return [(self.item_ids[i], similarities[i]) for i in similar_indices]


class HybridRecommender:
    """
    Hybrid recommender combining collaborative and content-based filtering.
    Uses weighted ensemble: alpha * CF + (1-alpha) * CBF
    """

    def __init__(self, alpha: float = 0.7):
        self.alpha = alpha
        self.cf = CollaborativeFilter()
        self.cbf = ContentFilter()
        self.scaler = MinMaxScaler()

    def fit(self, ratings_df: pd.DataFrame, items_df: pd.DataFrame):
        """Fit both models."""
        self.cf.fit(ratings_df)
        self.cbf.fit(items_df)
        logger.info(f"Hybrid recommender fitted (alpha={self.alpha})")

    def recommend(self, user_id: int, n: int = 10, seen_items: list = None) -> pd.DataFrame:
        """
        Get hybrid recommendations for a user.
        
        Returns:
            DataFrame with item_id, cf_score, cbf_score, hybrid_score
        """
        seen_items = seen_items or []

        # Collaborative filtering scores
        cf_recs = dict(self.cf.recommend(user_id, n=100, exclude_seen=seen_items))

        # Content-based scores (based on user's top-rated items)
        cbf_scores = {}
        for item_id in list(cf_recs.keys())[:20]:
            for sim_item, sim_score in self.cbf.similar_items(item_id, n=20):
                if sim_item not in seen_items:
                    cbf_scores[sim_item] = cbf_scores.get(sim_item, 0) + sim_score

        all_items = set(cf_recs.keys()) | set(cbf_scores.keys())
        results = []
        for item_id in all_items:
            cf_score = cf_recs.get(item_id, 0)
            cbf_score = cbf_scores.get(item_id, 0)
            hybrid_score = self.alpha * cf_score + (1 - self.alpha) * cbf_score
            results.append({'item_id': item_id, 'cf_score': cf_score,
                           'cbf_score': cbf_score, 'hybrid_score': hybrid_score})

        df = pd.DataFrame(results).sort_values('hybrid_score', ascending=False).head(n)
        return df.reset_index(drop=True)

    def evaluate(self, test_ratings: pd.DataFrame, k: int = 10) -> dict:
        """Evaluate model using Precision@K and Recall@K."""
        precisions, recalls = [], []

        for user_id in test_ratings['user_id'].unique():
            actual = set(test_ratings[test_ratings['user_id'] == user_id]['item_id'])
            recs = self.recommend(user_id, n=k)
            predicted = set(recs['item_id'].tolist())

            if predicted:
                precisions.append(len(actual & predicted) / len(predicted))
            if actual:
                recalls.append(len(actual & predicted) / len(actual))

        metrics = {
            f'precision@{k}': np.mean(precisions),
            f'recall@{k}': np.mean(recalls),
        }
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics


if __name__ == '__main__':
    np.random.seed(42)
    n_users, n_items = 200, 100

    # Sample ratings
    ratings = pd.DataFrame({
        'user_id': np.random.randint(0, n_users, 2000),
        'item_id': np.random.randint(0, n_items, 2000),
        'rating': np.random.randint(1, 6, 2000)
    }).drop_duplicates(['user_id', 'item_id'])

    # Sample items
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
    items = pd.DataFrame({
        'item_id': range(n_items),
        'description': [f'Product {i} description with features' for i in range(n_items)],
        'tags': [f'tag{i%5} tag{i%3}' for i in range(n_items)],
        'category': [categories[i % 5] for i in range(n_items)]
    })

    recommender = HybridRecommender(alpha=0.7)
    recommender.fit(ratings, items)

    recs = recommender.recommend(user_id=1, n=10)
    print(f"\nTop 10 recommendations for User 1:\n{recs}")