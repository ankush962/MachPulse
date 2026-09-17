from __future__ import annotations

import numpy as np

from ml.anomaly_detection.pipeline import (
    MachineAnalyzer,
)
from ml.features.extractor import (
    extract_features,
)


class MLService:

    def __init__(self) -> None:

        self.pipeline = MachineAnalyzer()

    def extract(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        sample_rate: float,
    ) -> dict[str, float]:

        return extract_features(
            x,
            y,
            z,
            sample_rate,
        )

    def analyze(
        self,
        machine_id: str,
        features: dict[str, float],
    ) -> dict:

        return self.pipeline.analyze(
            machine_id,
            features,
        )


analyzer = MLService()