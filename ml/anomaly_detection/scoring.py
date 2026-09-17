from __future__ import annotations

import numpy as np


def calculate_health_score(
    anomaly_score: float,
) -> float:

    anomaly_score = float(
        np.clip(anomaly_score, 0.0, 1.0)
    )

    health = 100.0 * (
        1.0 - anomaly_score
    )

    return round(
        float(np.clip(health, 0.0, 100.0)),
        1,
    )


def risk_level(
    health_score: float,
) -> str:

    if health_score >= 80:
        return "LOW"

    if health_score >= 60:
        return "MEDIUM"

    if health_score >= 40:
        return "HIGH"

    return "CRITICAL"