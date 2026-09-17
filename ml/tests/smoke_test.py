import numpy as np

from ml.features.extractor import extract_features


def main() -> None:

    sample_rate = 100

    t = np.arange(
        0,
        2.56,
        1 / sample_rate,
    )

    signal = (
        0.2
        * np.sin(
            2
            * np.pi
            * 8
            * t
        )
    )

    features = extract_features(
        signal,
        signal * 0.5,
        signal * 0.25,
        sample_rate,
    )

    print("Extracted features:")
    print(features)

    assert features["rms"] > 0
    assert features["dominant_frequency"] > 0

    print("ML smoke test passed.")


if __name__ == "__main__":
    main()