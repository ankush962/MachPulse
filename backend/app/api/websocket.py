from __future__ import annotations

import json
from typing import Any

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.services.ai_service import get_maintenance_advice
from backend.app.services.ml_service import analyzer


router = APIRouter()


class ConnectionManager:
    """
    Keeps track of all WebSocket clients connected
    to each machine.

    Example:

        M01
        ├── Android phone
        └── React dashboard
    """

    def __init__(self) -> None:
        self.connections: dict[
            str,
            set[WebSocket],
        ] = {}

    async def connect(
        self,
        machine_id: str,
        websocket: WebSocket,
    ) -> None:

        await websocket.accept()

        self.connections.setdefault(
            machine_id,
            set(),
        ).add(websocket)

        print(
            f"Client connected to {machine_id}. "
            f"Clients: "
            f"{len(self.connections[machine_id])}"
        )

    def disconnect(
        self,
        machine_id: str,
        websocket: WebSocket,
    ) -> None:

        clients = self.connections.get(
            machine_id
        )

        if clients is None:
            return

        clients.discard(websocket)

        if not clients:
            self.connections.pop(
                machine_id,
                None,
            )

        print(
            f"Client disconnected from {machine_id}."
        )

    async def broadcast(
        self,
        machine_id: str,
        message: dict[str, Any],
    ) -> None:

        clients = self.connections.get(
            machine_id,
            set(),
        )

        if not clients:
            return

        disconnected = []

        for client in list(clients):

            try:
                await client.send_json(
                    message
                )

            except Exception:
                disconnected.append(client)

        for client in disconnected:
            clients.discard(client)


manager = ConnectionManager()


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
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
            "message": (
                "accelerometer data missing"
            ),
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

    if sample_rate <= 0:
        sample_rate = 100

    if len(x) < 16:

        return {
            "status": "error",
            "message": (
                "not enough sensor samples"
            ),
        }

    if not (
        len(x)
        == len(y)
        == len(z)
    ):

        return {
            "status": "error",
            "message": (
                "sensor axis lengths differ"
            ),
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

    response: dict[str, Any] = {

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
        and ml_result.get(
            "health_score",
            100,
        ) < 70
    ):

        response["ai_advice"] = (
            get_maintenance_advice(
                machine_id,
                features,
                ml_result,
            )
        )

    print(
        f"[{machine_id}] "
        f"health={ml_result.get('health_score')} "
        f"risk={ml_result.get('risk')} "
        f"anomaly={ml_result.get('is_anomaly')}"
    )

    return response


@router.websocket(
    "/ws/monitor/{machine_id}"
)
async def monitor(
    websocket: WebSocket,
    machine_id: str,
):

    await manager.connect(
        machine_id,
        websocket,
    )

    try:

        await websocket.send_json(
            {
                "status": "connected",
                "machine_id": machine_id,
            }
        )

        while True:

            text = await websocket.receive_text()

            try:

                payload = json.loads(
                    text
                )

            except json.JSONDecodeError:

                await websocket.send_json(
                    {
                        "status": "error",
                        "message": "Invalid JSON",
                    }
                )

                continue

            try:

                response = await process_payload(
                    machine_id,
                    payload,
                )

                # Send the ML result to EVERY
                # client connected to this machine.
                #
                # Therefore:
                #
                # Android → FastAPI → React
                #                     ↓
                #                   Android

                await manager.broadcast(
                    machine_id,
                    response,
                )

            except Exception as exc:

                error_response = {
                    "status": "error",
                    "message": str(exc),
                }

                await websocket.send_json(
                    error_response
                )

    except WebSocketDisconnect:

        manager.disconnect(
            machine_id,
            websocket,
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

        from backend.app.services.demo_service import (
            stream_demo,
        )

        await stream_demo(
            websocket,
            machine_id,
        )

    except WebSocketDisconnect:

        print(
            f"Demo machine {machine_id} disconnected."
        )