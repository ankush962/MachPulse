from __future__ import annotations

import numpy as np


def calculate_rms(signal: np.ndarray) -> float:

    signal = np.asarray(signal, dtype=float)

    if signal.size == 0:
        raise ValueError("Signal cannot be empty.")

    return float(
        np.sqrt(np.mean(np.square(signal)))
    )