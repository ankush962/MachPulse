from __future__ import annotations

import numpy as np


def calculate_fft(
    signal: np.ndarray,
    sample_rate: float,
) -> tuple[np.ndarray, np.ndarray]:

    signal = np.asarray(signal, dtype=float)

    if signal.size == 0:
        raise ValueError("Signal cannot be empty.")

    if sample_rate <= 0:
        raise ValueError(
            "Sample rate must be greater than zero."
        )

    centered = signal - np.mean(signal)

    spectrum = np.fft.rfft(centered)

    frequencies = np.fft.rfftfreq(
        len(centered),
        d=1.0 / sample_rate,
    )

    magnitude = np.abs(spectrum)

    return frequencies, magnitude


def dominant_frequency(
    signal: np.ndarray,
    sample_rate: float,
) -> float:

    frequencies, magnitude = calculate_fft(
        signal,
        sample_rate,
    )

    if len(magnitude) <= 1:
        return 0.0

    index = np.argmax(magnitude[1:]) + 1

    return float(frequencies[index])