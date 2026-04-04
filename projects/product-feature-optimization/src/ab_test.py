"""
A/B Testing Engine
Core statistical testing framework for product experiments.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from dataclasses import dataclass
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExperimentResult:
    experiment_name: str
    control_size: int
    treatment_size: int
    control_rate: float
    treatment_rate: float
    relative_lift: float
    p_value: float
    confidence_interval: tuple
    is_significant: bool
    test_type: str
    power: float


def calculate_sample_size(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> int:
    """
    Calculate required sample size per variant using power analysis.
    
    Args:
        baseline_rate: Current conversion rate (e.g. 0.05 for 5%)
        minimum_detectable_effect: Smallest lift worth detecting (e.g. 0.10 for 10%)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)
    
    Returns:
        Required sample size per variant
    """
    treatment_rate = baseline_rate * (1 + minimum_detectable_effect)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    p_avg = (baseline_rate + treatment_rate) / 2
    
    n = (
        (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) +
         z_beta * np.sqrt(baseline_rate * (1 - baseline_rate) + treatment_rate * (1 - treatment_rate))) ** 2
        / (treatment_rate - baseline_rate) ** 2
    )
    
    sample_size = int(np.ceil(n))
    logger.info(f"Required sample size per variant: {sample_size:,}")
    return sample_size


def run_proportion_test(
    control_conversions: int,
    control_visitors: int,
    treatment_conversions: int,
    treatment_visitors: int,
    experiment_name: str = "Experiment",
    alpha: float = 0.05
) -> ExperimentResult:
    """
    Run a two-proportion z-test for conversion rate experiments.
    
    Args:
        control_conversions: Number of conversions in control group
        control_visitors: Total visitors in control group
        treatment_conversions: Number of conversions in treatment group
        treatment_visitors: Total visitors in treatment group
        experiment_name: Name of the experiment
        alpha: Significance level
    
    Returns:
        ExperimentResult with all statistics
    """
    control_rate = control_conversions / control_visitors
    treatment_rate = treatment_conversions / treatment_visitors
    relative_lift = (treatment_rate - control_rate) / control_rate

    # Two-proportion z-test
    count = np.array([treatment_conversions, control_conversions])
    nobs = np.array([treatment_visitors, control_visitors])
    
    from statsmodels.stats.proportion import proportions_ztest, proportion_confint
    z_stat, p_value = proportions_ztest(count, nobs)
    
    # Confidence interval for the difference
    ci_low, ci_high = proportion_confint(treatment_conversions, treatment_visitors, alpha=alpha)
    ci_control_low, ci_control_high = proportion_confint(control_conversions, control_visitors, alpha=alpha)
    
    diff_ci = (
        (ci_low - ci_control_high),
        (ci_high - ci_control_low)
    )

    is_significant = p_value < alpha

    # Observed power
    effect_size = abs(treatment_rate - control_rate) / np.sqrt(
        (control_rate * (1 - control_rate) + treatment_rate * (1 - treatment_rate)) / 2
    )
    power = stats.norm.cdf(abs(z_stat) - stats.norm.ppf(1 - alpha / 2))

    result = ExperimentResult(
        experiment_name=experiment_name,
        control_size=control_visitors,
        treatment_size=treatment_visitors,
        control_rate=control_rate,
        treatment_rate=treatment_rate,
        relative_lift=relative_lift,
        p_value=p_value,
        confidence_interval=diff_ci,
        is_significant=is_significant,
        test_type="Two-Proportion Z-Test",
        power=power
    )

    _log_result(result)
    return result


def _log_result(result: ExperimentResult):
    """Log experiment results."""
    status = "✅ SIGNIFICANT" if result.is_significant else "❌ NOT SIGNIFICANT"
    logger.info(f"""
    ═══════════════════════════════════════
    Experiment: {result.experiment_name}
    ───────────────────────────────────────
    Control Rate:   {result.control_rate:.2%} (n={result.control_size:,})
    Treatment Rate: {result.treatment_rate:.2%} (n={result.treatment_size:,})
    Relative Lift:  {result.relative_lift:+.1%}
    P-Value:        {result.p_value:.4f}
    95% CI:         ({result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f})
    Power:          {result.power:.2%}
    Result:         {status}
    ═══════════════════════════════════════
    """)


def plot_experiment_results(result: ExperimentResult, output_path: str = 'experiment_results.html'):
    """Create interactive Plotly visualization of experiment results."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Conversion Rates', 'Relative Lift'),
        specs=[[{"type": "bar"}, {"type": "indicator"}]]
    )

    colors = ['#6366f1', '#ec4899'] if result.is_significant else ['#6366f1', '#94a3b8']

    fig.add_trace(go.Bar(
        x=['Control', 'Treatment'],
        y=[result.control_rate * 100, result.treatment_rate * 100],
        marker_color=colors,
        text=[f"{result.control_rate:.2%}", f"{result.treatment_rate:.2%}"],
        textposition='outside',
        name='Conversion Rate'
    ), row=1, col=1)

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=result.treatment_rate * 100,
        delta={
            'reference': result.control_rate * 100,
            'relative': True,
            'valueformat': '.1%'
        },
        title={'text': f"Lift: {result.relative_lift:+.1%}<br>p={result.p_value:.4f}"},
        number={'suffix': '%', 'valueformat': '.2f'}
    ), row=1, col=2)

    status = "SIGNIFICANT ✅" if result.is_significant else "NOT SIGNIFICANT ❌"
    fig.update_layout(
        title=f"{result.experiment_name} — {status}",
        template='plotly_dark',
        height=400
    )

    fig.write_html(output_path)
    logger.info(f"Results chart saved to {output_path}")


if __name__ == '__main__':
    # Example: Checkout flow optimization experiment
    print("Sample size needed:", calculate_sample_size(
        baseline_rate=0.05,
        minimum_detectable_effect=0.10
    ))

    result = run_proportion_test(
        control_conversions=1250,
        control_visitors=25000,
        treatment_conversions=1750,
        treatment_visitors=25000,
        experiment_name="Checkout Flow Redesign"
    )

    plot_experiment_results(result)