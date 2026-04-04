"""
Anomaly Detection Engine
Detects anomalies in real-time metric streams using Z-score and IQR methods.
"""

import numpy as np
from collections import deque
from typing import Tuple


class AnomalyDetector:
    """
    Detects anomalies in streaming time-series data.
    Uses Z-score with a rolling window for real-time detection.
    """

    def __init__(self, window_size: int = 30, z_threshold: float = 2.5):
        self.window_size = window_size
        self.z_threshold = z_threshold

    def detect(self, values: list) -> Tuple[bool, float]:
        """
        Detect if the latest value is anomalous.
        
        Args:
            values: List of recent metric values (latest is last)
        
        Returns:
            (is_anomaly, z_score)
        """
        if len(values) < 5:
            return False, 0.0

        window = values[-self.window_size:]
        latest = window[-1]
        history = window[:-1]

        mean = np.mean(history)
        std = np.std(history)

        if std == 0:
            return False, 0.0

        z_score = (latest - mean) / std
        is_anomaly = abs(z_score) > self.z_threshold

        return is_anomaly, round(z_score, 3)

    def detect_iqr(self, values: list) -> Tuple[bool, float]:
        """
        Alternative IQR-based anomaly detection (more robust to outliers).
        
        Returns:
            (is_anomaly, iqr_score)
        """
        if len(values) < 5:
            return False, 0.0

        window = np.array(values[-self.window_size:])
        latest = window[-1]
        history = window[:-1]

        q1 = np.percentile(history, 25)
        q3 = np.percentile(history, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        is_anomaly = latest < lower_bound or latest > upper_bound
        iqr_score = (latest - np.median(history)) / (iqr + 1e-9)

        return is_anomaly, round(iqr_score, 3)