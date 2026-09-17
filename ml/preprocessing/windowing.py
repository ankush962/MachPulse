from __future__ import annotations

import numpy as np


def create_windows(
    signal: np.ndarray,
    window_size: int = 256,
    step: int = 256,
) -> list[np.ndarray]:

    signal = np.asarray(signal, dtype=float)

    if signal.size < window_size:
        return []

    windows = []

    for start in range(
        0,
        signal.size - window_size + 1,
        step,
    ):
        end = start + window_size
        windows.append(signal[start:end])

    return windows