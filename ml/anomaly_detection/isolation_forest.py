from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


FEATURE_NAMES = [
    "rms",
    "std",
    "crest_factor",
    "dominant_frequency",
    "spectral_energy",
]


class IsolationForestDetector:

    def __init__(self) -> None:

        self.scaler = StandardScaler()

        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.08,
            random_state=42,
        )

        self.is_fitted = False

    def fit(
        self,
        feature_rows: list[dict[str, float]],
    ) -> None:

        if len(feature_rows) < 10:
            raise ValueError(
                "At least 10 baseline samples are required."
            )

        matrix = np.array(
            [
                [
                    row[name]
                    for name in FEATURE_NAMES
                ]
                for row in feature_rows
            ],
            dtype=float,
        )

        scaled = self.scaler.fit_transform(matrix)

        self.model.fit(scaled)

        self.is_fitted = True

    def predict(
        self,
        features: dict[str, float],
    ) -> dict[str, float | bool]:

        if not self.is_fitted:
            raise RuntimeError(
                "Detector has not been fitted."
            )

        vector = np.array(
            [
                [
                    features[name]
                    for name in FEATURE_NAMES
                ]
            ],
            dtype=float,
        )

        scaled = self.scaler.transform(vector)

        prediction = int(
            self.model.predict(scaled)[0]
        )

        decision = float(
            self.model.decision_function(scaled)[0]
        )

        # Heuristic conversion for the hackathon MVP.
        anomaly_score = float(
            np.clip(
                (0.15 - decision) / 0.30,
                0.0,
                1.0,
            )
        )

        if prediction == -1:
            anomaly_score = max(
                anomaly_score,
                0.75,
            )

        return {
            "is_anomaly": prediction == -1,
            "decision_score": decision,
            "anomaly_score": anomaly_score,
        }