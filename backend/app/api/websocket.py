from __future__ import annotations

import json
from typing import Any

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.demo_service import stream_demo
from backend.app.services.ai_service import get_maintenance_advice
from backend.app.services.ml_service import analyzer


router = APIRouter()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


async def process_payload(
    machine_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:

    accelerometer = payload.get(
        "accelerometer"
    )

    if not accelerometer:
        return {
            "status": "error",
            "message": "accelerometer data missing",
        }

    x = np.asarray(
        accelerometer.get("x", []),
        dtype=float,
    )

    y = np.asarray(
        accelerometer.get("y", []),
        dtype=float,
    )

    z = np.asarray(
        accelerometer.get("z", []),
        dtype=float,
    )

    sample_rate = safe_float(
        payload.get(
            "sample_rate",
            100,
        ),
        100,
    )

    if len(x) < 16:
        return {
            "status": "error",
            "message": "not enough sensor samples",
        }

    if not (
        len(x)
        == len(y)
        == len(z)
    ):
        return {
            "status": "error",
            "message": "sensor axis lengths differ",
        }

    features = analyzer.extract(
        x,
        y,
        z,
        sample_rate,
    )

    ml_result = analyzer.analyze(
        machine_id,
        features,
    )

    response = {
        "status": "ok",
        "machine_id": machine_id,
        "timestamp": payload.get(
            "timestamp"
        ),
        "features": features,
        "analysis": ml_result,
        "ai_advice": None,
    }

    if (
        ml_result.get("is_anomaly")
        and ml_result.get("health_score", 100) < 70
    ):
        response["ai_advice"] = (
            get_maintenance_advice(
                machine_id,
                features,
                ml_result,
            )
        )

    return response


@router.websocket(
    "/ws/monitor/{machine_id}"
)
async def monitor(
    websocket: WebSocket,
    machine_id: str,
):

    await websocket.accept()

    await websocket.send_json(
        {
            "status": "connected",
            "machine_id": machine_id,
        }
    )

    try:

        while True:

            text = await websocket.receive_text()

            try:
                payload = json.loads(text)

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "status": "error",
                        "message": "invalid JSON",
                    }
                )
                continue

            try:

                response = await process_payload(
                    machine_id,
                    payload,
                )

                await websocket.send_json(
                    response
                )

            except Exception as exc:

                await websocket.send_json(
                    {
                        "status": "error",
                        "message": str(exc),
                    }
                )

    except WebSocketDisconnect:

        print(
            f"Machine {machine_id} disconnected."
        )



@router.websocket(
    "/ws/demo/{machine_id}"
)
async def demo_monitor(
    websocket: WebSocket,
    machine_id: str,
):

    await websocket.accept()

    await websocket.send_json(
        {
            "status": "connected",
            "machine_id": machine_id,
            "demo": True,
        }
    )

    try:

        await stream_demo(
            websocket,
            machine_id,
        )

    except WebSocketDisconnect:

        print(
            f"Demo machine {machine_id} disconnected."
        )