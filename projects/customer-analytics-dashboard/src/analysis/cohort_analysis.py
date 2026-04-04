"""
Cohort Analysis
Tracks customer retention and behavior patterns across cohorts over time.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_cohort_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a cohort retention table.
    
    Args:
        df: DataFrame with columns [customer_id, signup_date, event_date]
    
    Returns:
        Pivot table showing retention % by cohort month and period
    """
    df = df.copy()
    df['signup_month'] = df['signup_date'].dt.to_period('M')
    df['event_month'] = df['event_date'].dt.to_period('M')
    df['period'] = (df['event_month'] - df['signup_month']).apply(lambda x: x.n)

    cohort_data = (
        df.groupby(['signup_month', 'period'])['customer_id']
        .nunique()
        .reset_index()
        .rename(columns={'customer_id': 'customers'})
    )

    cohort_sizes = cohort_data[cohort_data['period'] == 0].set_index('signup_month')['customers']

    cohort_table = cohort_data.pivot_table(
        index='signup_month', columns='period', values='customers'
    )

    retention_table = cohort_table.divide(cohort_sizes, axis=0) * 100
    return retention_table.round(1)


def plot_cohort_heatmap(retention_table: pd.DataFrame, output_path: str = 'cohort_heatmap.png'):
    """Plot cohort retention heatmap."""
    plt.figure(figsize=(16, 8))
    sns.heatmap(
        retention_table,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd_r',
        linewidths=0.5,
        cbar_kws={'label': 'Retention %'}
    )
    plt.title('Customer Cohort Retention Analysis', fontsize=16, fontweight='bold')
    plt.xlabel('Months Since Signup', fontsize=12)
    plt.ylabel('Cohort (Signup Month)', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    logger.info(f"Cohort heatmap saved to {output_path}")
    plt.close()


def calculate_retention_metrics(retention_table: pd.DataFrame) -> dict:
    """Calculate key retention metrics."""
    metrics = {
        'avg_month1_retention': retention_table[1].mean() if 1 in retention_table.columns else 0,
        'avg_month3_retention': retention_table[3].mean() if 3 in retention_table.columns else 0,
        'avg_month6_retention': retention_table[6].mean() if 6 in retention_table.columns else 0,
        'best_cohort': retention_table[1].idxmax() if 1 in retention_table.columns else None,
        'worst_cohort': retention_table[1].idxmin() if 1 in retention_table.columns else None,
    }
    logger.info(f"Retention Metrics: {metrics}")
    return metrics


if __name__ == '__main__':
    # Generate sample data
    np.random.seed(42)
    n_customers = 500
    customers = pd.DataFrame({
        'customer_id': range(n_customers),
        'signup_date': pd.date_range('2023-01-01', periods=n_customers, freq='D')
    })

    # Simulate events with decreasing retention over time
    events = []
    for _, row in customers.iterrows():
        for month in range(12):
            if np.random.random() < max(0.1, 0.9 - month * 0.08):
                events.append({
                    'customer_id': row['customer_id'],
                    'signup_date': row['signup_date'],
                    'event_date': row['signup_date'] + pd.DateOffset(months=month)
                })

    events_df = pd.DataFrame(events)
    retention = build_cohort_table(events_df)
    plot_cohort_heatmap(retention)
    metrics = calculate_retention_metrics(retention)
    print(f"\nAverage Month-1 Retention: {metrics['avg_month1_retention']:.1f}%")
    print(f"Average Month-3 Retention: {metrics['avg_month3_retention']:.1f}%")
    print(f"Average Month-6 Retention: {metrics['avg_month6_retention']:.1f}%")