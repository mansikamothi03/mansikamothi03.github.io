"""
Customer Lifetime Value (CLV) Prediction Model
Predicts future revenue per customer using BG/NBD and Gamma-Gamma models.
"""

import pandas as pd
import numpy as np
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_transactions(filepath: str) -> pd.DataFrame:
    """Load transaction data from CSV."""
    df = pd.read_csv(filepath, parse_dates=['order_date'])
    logger.info(f"Loaded {len(df)} transactions from {df['customer_id'].nunique()} customers")
    return df


def build_rfm_summary(df: pd.DataFrame, observation_period_end: str) -> pd.DataFrame:
    """
    Build RFM summary table required for CLV modeling.
    
    Returns DataFrame with: frequency, recency, T (age), monetary_value
    """
    summary = summary_data_from_transaction_data(
        df,
        customer_id_col='customer_id',
        datetime_col='order_date',
        monetary_value_col='order_value',
        observation_period_end=observation_period_end,
        freq='D'
    )
    logger.info(f"RFM summary built for {len(summary)} customers")
    return summary


def fit_bg_nbd_model(summary: pd.DataFrame) -> BetaGeoFitter:
    """
    Fit BG/NBD model to predict future purchase frequency.
    BG/NBD = Beta-Geometric / Negative Binomial Distribution
    """
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(
        summary['frequency'],
        summary['recency'],
        summary['T']
    )
    logger.info(f"BG/NBD model fitted. Params: {bgf.params_}")
    return bgf


def fit_gamma_gamma_model(summary: pd.DataFrame) -> GammaGammaFitter:
    """
    Fit Gamma-Gamma model to predict average transaction value.
    Only uses customers with repeat purchases.
    """
    returning_customers = summary[summary['frequency'] > 0]
    ggf = GammaGammaFitter(penalizer_coef=0.001)
    ggf.fit(
        returning_customers['frequency'],
        returning_customers['monetary_value']
    )
    logger.info(f"Gamma-Gamma model fitted. Params: {ggf.params_}")
    return ggf


def predict_clv(
    summary: pd.DataFrame,
    bgf: BetaGeoFitter,
    ggf: GammaGammaFitter,
    time_horizon_months: int = 12,
    discount_rate: float = 0.01
) -> pd.DataFrame:
    """
    Predict Customer Lifetime Value over a given time horizon.
    
    Args:
        summary: RFM summary DataFrame
        bgf: Fitted BG/NBD model
        ggf: Fitted Gamma-Gamma model
        time_horizon_months: Prediction window in months
        discount_rate: Monthly discount rate for NPV calculation
    
    Returns:
        DataFrame with CLV predictions per customer
    """
    clv = ggf.customer_lifetime_value(
        bgf,
        summary['frequency'],
        summary['recency'],
        summary['T'],
        summary['monetary_value'],
        time=time_horizon_months,
        discount_rate=discount_rate,
        freq='D'
    )

    results = summary.copy()
    results['predicted_clv'] = clv
    results['predicted_purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(
        time_horizon_months * 30,
        summary['frequency'],
        summary['recency'],
        summary['T']
    )
    results['clv_segment'] = pd.qcut(
        results['predicted_clv'],
        q=4,
        labels=['Bronze', 'Silver', 'Gold', 'Platinum']
    )

    logger.info(f"\nCLV Summary:\n{results['predicted_clv'].describe()}")
    logger.info(f"\nSegment Distribution:\n{results['clv_segment'].value_counts()}")
    return results


def plot_clv_distribution(results: pd.DataFrame, output_path: str = 'clv_distribution.png'):
    """Plot CLV distribution by segment."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # CLV distribution
    axes[0].hist(results['predicted_clv'], bins=50, color='#8b5cf6', edgecolor='white', alpha=0.8)
    axes[0].set_title('CLV Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Predicted CLV ($)')
    axes[0].set_ylabel('Number of Customers')

    # Segment breakdown
    segment_clv = results.groupby('clv_segment')['predicted_clv'].mean()
    colors = ['#94a3b8', '#60a5fa', '#f59e0b', '#8b5cf6']
    axes[1].bar(segment_clv.index, segment_clv.values, color=colors)
    axes[1].set_title('Average CLV by Segment', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Segment')
    axes[1].set_ylabel('Average CLV ($)')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    logger.info(f"CLV distribution plot saved to {output_path}")
    plt.close()


if __name__ == '__main__':
    # Generate sample transaction data
    np.random.seed(42)
    n_customers = 500
    transactions = []
    for cid in range(n_customers):
        n_orders = np.random.poisson(3)
        for _ in range(max(1, n_orders)):
            transactions.append({
                'customer_id': cid,
                'order_date': pd.Timestamp('2023-01-01') + pd.Timedelta(days=np.random.randint(0, 365)),
                'order_value': np.random.lognormal(mean=4.0, sigma=0.8)
            })

    df = pd.DataFrame(transactions)
    df.to_csv('data/transactions.csv', index=False)

    summary = build_rfm_summary(df, '2024-01-01')
    bgf = fit_bg_nbd_model(summary)
    ggf = fit_gamma_gamma_model(summary)
    results = predict_clv(summary, bgf, ggf, time_horizon_months=12)
    plot_clv_distribution(results)

    print(f"\nTop 10 Highest CLV Customers:")
    print(results.nlargest(10, 'predicted_clv')[['predicted_clv', 'clv_segment', 'frequency', 'monetary_value']])