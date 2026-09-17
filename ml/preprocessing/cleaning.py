from __future__ import annotations

import numpy as np


def clean_signal(signal: np.ndarray) -> np.ndarray:
    signal = np.asarray(signal, dtype=float)

    if signal.size == 0:
        raise ValueError("Signal cannot be empty.")

    signal = np.nan_to_num(
        signal,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    return signal