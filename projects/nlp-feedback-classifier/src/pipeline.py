"""
pipeline.py
-----------
End-to-end pipeline runner for the NLP Customer Feedback Classifier.

Usage:
    python src/pipeline.py --input data/raw/feedback.csv --output data/processed/
    python src/pipeline.py --input data/raw/feedback.csv --use-gpt --output data/processed/
"""

import argparse
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocess import preprocess_dataframe
from src.embed import embed_dataframe
from src.classify import classify_themes, print_theme_distribution
from src.cluster import find_optimal_k, cluster_embeddings, get_cluster_representatives
from src.sentiment import score_sentiment, sentiment_by_theme
from src.report import build_theme_report, export_report, print_console_summary, plot_theme_volume, plot_sentiment_heatmap


def run_pipeline(
    input_path: str,
    output_dir: str = "data/processed",
    text_col: str = "feedback_text",
    use_gpt_sentiment: bool = False,
    run_clustering: bool = True,
    save_plots: bool = True,
) -> pd.DataFrame:
    """
    Full pipeline:
    1. Load raw feedback CSV
    2. Preprocess (clean, deduplicate, lemmatize)
    3. Generate OpenAI embeddings
    4. Classify into product themes
    5. Cluster semantically similar responses
    6. Score sentiment (VADER + optional GPT-4o)
    7. Build and export theme report
    """
    print("\n" + "=" * 60)
    print("  NLP CUSTOMER FEEDBACK CLASSIFIER — PIPELINE START")
    print("=" * 60)

    # Step 1: Load
    print(f"\n[1/7] Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} records.")

    # Step 2: Preprocess
    print("\n[2/7] Preprocessing...")
    df = preprocess_dataframe(df, text_col=text_col, lemmatize_text=True)

    # Step 3: Embed
    print("\n[3/7] Generating embeddings...")
    os.makedirs(output_dir, exist_ok=True)
    embeddings_path = os.path.join(output_dir, "embeddings.npy")
    df, embeddings = embed_dataframe(df, text_col="cleaned_text", save_path=embeddings_path)

    # Step 4: Classify themes
    print("\n[4/7] Classifying themes...")
    df = classify_themes(df, embeddings)
    print_theme_distribution(df)

    # Step 5: Cluster
    if run_clustering:
        print("\n[5/7] Clustering...")
        best_k, scores = find_optimal_k(embeddings, k_min=3, k_max=12)
        labels, kmeans = cluster_embeddings(embeddings, k=best_k)
        df["cluster"] = labels

        reps = get_cluster_representatives(df, embeddings, kmeans, text_col=text_col)
        reps_path = os.path.join(output_dir, "cluster_representatives.csv")
        reps.to_csv(reps_path, index=False)
        print(f"  Cluster representatives saved: {reps_path}")

        if save_plots:
            from src.cluster import plot_clusters, plot_silhouette_scores
            plot_clusters(embeddings, labels, save_path=os.path.join(output_dir, "cluster_plot.png"))
            plot_silhouette_scores(range(3, 13), scores, best_k, save_path=os.path.join(output_dir, "silhouette_scores.png"))
    else:
        print("\n[5/7] Clustering skipped.")

    # Step 6: Sentiment
    print("\n[6/7] Scoring sentiment...")
    df = score_sentiment(df, text_col="cleaned_text", use_gpt=use_gpt_sentiment)
    print("\nSentiment by theme:")
    print(sentiment_by_theme(df).to_string())

    # Step 7: Report
    print("\n[7/7] Building report...")
    report = build_theme_report(df)
    print_console_summary(report)
    export_report(df, report, output_dir=output_dir)

    if save_plots:
        plot_theme_volume(report, save_path=os.path.join(output_dir, "theme_volume.png"))
        plot_sentiment_heatmap(report, save_path=os.path.join(output_dir, "sentiment_heatmap.png"))

    print("\n✅ Pipeline complete.")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NLP Customer Feedback Classifier Pipeline")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", default="data/processed", help="Output directory")
    parser.add_argument("--text-col", default="feedback_text", help="Column name containing feedback text")
    parser.add_argument("--use-gpt", action="store_true", help="Use GPT-4o for nuanced sentiment scoring")
    parser.add_argument("--no-clustering", action="store_true", help="Skip clustering step")
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")

    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        output_dir=args.output,
        text_col=args.text_col,
        use_gpt_sentiment=args.use_gpt,
        run_clustering=not args.no_clustering,
        save_plots=not args.no_plots,
    )