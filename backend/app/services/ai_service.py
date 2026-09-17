from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2",
)


def fallback_advice(
    features: dict,
    analysis: dict,
) -> str:

    rms = features.get(
        "rms",
        0,
    )

    frequency = features.get(
        "dominant_frequency",
        0,
    )

    if frequency > 20:
        return (
            "Abnormal vibration frequency detected. "
            "Inspect rotating components, bearings, "
            "alignment, and looseness."
        )

    if rms > 1.0:
        return (
            "Vibration level is elevated. "
            "Inspect machine mounting, fasteners, "
            "bearings, and rotating components."
        )

    return (
        "Machine health has degraded. "
        "Inspect for unusual vibration, "
        "loose components, and bearing wear."
    )


def get_maintenance_advice(
    machine_id: str,
    features: dict,
    analysis: dict,
) -> str:

    prompt = f"""
You are a predictive maintenance assistant.

Machine: {machine_id}

Sensor features:
{json.dumps(features, indent=2)}

ML analysis:
{json.dumps(analysis, indent=2)}

Give practical maintenance advice for a small workshop.

Return:
1. Likely issue
2. What to inspect
3. Immediate action

Keep the answer under 100 words.
Do not pretend to know the exact failed component.
"""

    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(
        body
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=8,
        ) as response:

            raw = response.read()

            result = json.loads(
                raw.decode("utf-8")
            )

            text = result.get(
                "response",
                "",
            ).strip()

            if text:
                return text

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        pass

    return fallback_advice(
        features,
        analysis,
    )