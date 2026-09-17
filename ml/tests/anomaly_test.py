import numpy as np

from ml.anomaly_detection.pipeline import MachineAnalyzer
from ml.features.extractor import extract_features


def make_signal(
    frequency: float,
    amplitude: float,
    sample_rate: int = 100,
    duration: float = 2.56,
):
    t = np.arange(
        0,
        duration,
        1 / sample_rate,
    )

    signal = (
        amplitude
        * np.sin(
            2 * np.pi * frequency * t
        )
    )

    signal += np.random.normal(
        0,
        0.02,
        len(t),
    )

    return signal


def get_features(
    frequency: float,
    amplitude: float,
):
    signal = make_signal(
        frequency,
        amplitude,
    )

    return extract_features(
        signal,
        signal * 0.5,
        signal * 0.25,
        100,
    )


def main():

    analyzer = MachineAnalyzer()

    # Healthy baseline
    for _ in range(12):

        features = get_features(
            frequency=8,
            amplitude=0.15,
        )

        result = analyzer.analyze(
            "M01",
            features,
        )

        print(
            "Baseline:",
            result,
        )

    print("\n--- Testing abnormal signal ---\n")

    abnormal_features = get_features(
        frequency=28,
        amplitude=0.75,
    )

    result = analyzer.analyze(
        "M01",
        abnormal_features,
    )

    print("Abnormal result:")
    print(result)


if __name__ == "__main__":
    main()