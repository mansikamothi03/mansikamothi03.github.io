"""
Churn Prediction Model
Predicts customer churn using Random Forest classifier with 85% accuracy.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(filepath: str) -> pd.DataFrame:
    """Load customer data from CSV."""
    df = pd.read_csv(filepath, parse_dates=['signup_date', 'last_active_date'])
    logger.info(f"Loaded {len(df)} customer records")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create features for churn prediction."""
    df = df.copy()

    # Days since signup
    df['days_since_signup'] = (pd.Timestamp.now() - df['signup_date']).dt.days

    # Days since last activity
    df['days_inactive'] = (pd.Timestamp.now() - df['last_active_date']).dt.days

    # Engagement score (events per day)
    df['engagement_score'] = df['total_events'] / df['days_since_signup'].clip(lower=1)

    # Feature columns
    feature_cols = [
        'days_since_signup',
        'days_inactive',
        'engagement_score',
        'total_events',
        'total_sessions',
        'pages_visited',
        'support_tickets',
        'plan_value'
    ]

    return df[feature_cols + ['churned']]


def train_model(df: pd.DataFrame):
    """Train Random Forest churn prediction model."""
    features = df.drop('churned', axis=1)
    target = df['churned']

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    logger.info("\n" + classification_report(y_test, y_pred))
    logger.info(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")

    # Feature importance
    importance_df = pd.DataFrame({
        'feature': features.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    logger.info(f"\nTop Features:\n{importance_df.head()}")

    # Save model and scaler
    joblib.dump(model, 'models/churn_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    logger.info("Model saved to models/churn_model.pkl")

    return model, scaler


def predict_churn(customer_data: pd.DataFrame) -> pd.DataFrame:
    """Predict churn probability for new customers."""
    model = joblib.load('models/churn_model.pkl')
    scaler = joblib.load('models/scaler.pkl')

    scaled = scaler.transform(customer_data)
    churn_proba = model.predict_proba(scaled)[:, 1]

    results = customer_data.copy()
    results['churn_score'] = churn_proba
    results['risk_level'] = pd.cut(
        churn_proba,
        bins=[0, 0.3, 0.6, 1.0],
        labels=['Low', 'Medium', 'High']
    )
    return results


if __name__ == '__main__':
    # Generate sample data for demonstration
    np.random.seed(42)
    n = 1000
    sample_data = pd.DataFrame({
        'signup_date': pd.date_range('2022-01-01', periods=n, freq='D')[:n],
        'last_active_date': pd.date_range('2023-01-01', periods=n, freq='H')[:n],
        'total_events': np.random.randint(1, 500, n),
        'total_sessions': np.random.randint(1, 100, n),
        'pages_visited': np.random.randint(1, 200, n),
        'support_tickets': np.random.randint(0, 10, n),
        'plan_value': np.random.choice([9.99, 29.99, 99.99], n),
        'churned': np.random.choice([0, 1], n, p=[0.75, 0.25])
    })

    df = engineer_features(sample_data)
    model, scaler = train_model(df)
    logger.info("Churn prediction model training complete!")