from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ml.anomaly_detection.isolation_forest import (
    IsolationForestDetector,
)
from ml.anomaly_detection.scoring import (
    calculate_health_score,
    risk_level,
)


@dataclass
class MachineState:
    baseline: list[dict[str, float]] = field(
        default_factory=list
    )

    detector: IsolationForestDetector = field(
        default_factory=IsolationForestDetector
    )

    calibrated: bool = False


class MachineAnalyzer:

    CALIBRATION_WINDOWS = 10

    def __init__(self) -> None:

        self.machines: dict[
            str,
            MachineState
        ] = {}

    def _get_machine(
        self,
        machine_id: str,
    ) -> MachineState:

        if machine_id not in self.machines:
            self.machines[machine_id] = MachineState()

        return self.machines[machine_id]

    def analyze(
        self,
        machine_id: str,
        features: dict[str, float],
    ) -> dict[str, Any]:

        state = self._get_machine(machine_id)

        if not state.calibrated:

            state.baseline.append(features)

            if (
                len(state.baseline)
                >= self.CALIBRATION_WINDOWS
            ):
                state.detector.fit(
                    state.baseline
                )

                state.calibrated = True

                baseline_complete = True

            else:
                baseline_complete = False

            remaining = max(
                self.CALIBRATION_WINDOWS
                - len(state.baseline),
                0,
            )

            return {
                "status": "calibrating",
                "calibrated": baseline_complete,
                "calibration_progress": len(
                    state.baseline
                ),
                "calibration_total":
                    self.CALIBRATION_WINDOWS,
                "remaining_windows": remaining,
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "health_score": 100.0,
                "risk": "LOW",
            }

        prediction = state.detector.predict(
            features
        )

        anomaly_score = float(
            prediction["anomaly_score"]
        )

        health_score = calculate_health_score(
            anomaly_score
        )

        return {
            "status": "monitoring",
            "calibrated": True,
            "is_anomaly": bool(
                prediction["is_anomaly"]
            ),
            "anomaly_score": round(
                anomaly_score,
                3,
            ),
            "health_score": health_score,
            "risk": risk_level(
                health_score
            ),
            "decision_score": round(
                float(
                    prediction["decision_score"]
                ),
                4,
            ),
        }

    def reset(
        self,
        machine_id: str,
    ) -> None:

        self.machines.pop(
            machine_id,
            None,
        )