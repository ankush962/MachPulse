from __future__ import annotations

import numpy as np

from ml.features.fft import dominant_frequency
from ml.features.rms import calculate_rms


def extract_features(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    sample_rate: float,
) -> dict[str, float]:

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    if not (
        len(x) == len(y) == len(z)
    ):
        raise ValueError(
            "Accelerometer axes must have equal length."
        )

    if len(x) < 16:
        raise ValueError(
            "Not enough samples for feature extraction."
        )

    # Remove gravity/DC component.
    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)
    z_centered = z - np.mean(z)

    magnitude = np.sqrt(
        x_centered**2
        + y_centered**2
        + z_centered**2
    )

    rms = calculate_rms(magnitude)

    standard_deviation = float(
        np.std(magnitude)
    )

    peak = float(
        np.max(np.abs(magnitude))
    )

    crest_factor = (
        peak / rms
        if rms > 1e-9
        else 0.0
    )

    frequency = dominant_frequency(
        magnitude,
        sample_rate,
    )

    spectral_energy = float(
        np.mean(
            np.square(
                np.abs(
                    np.fft.rfft(
                        magnitude
                    )
                )
            )
        )
    )

    return {
        "rms": rms,
        "std": standard_deviation,
        "crest_factor": crest_factor,
        "dominant_frequency": frequency,
        "spectral_energy": spectral_energy,
    }