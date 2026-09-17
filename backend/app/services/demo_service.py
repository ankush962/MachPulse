from __future__ import annotations

import asyncio
import time

import numpy as np




async def stream_demo(websocket, machine_id: str):

    from backend.app.api.websocket import process_payload
    
    sample_rate = 100
    samples = 256

    step = 0

    while True:

        step += 1

        if step <= 12:
            mode = "healthy"

        elif step <= 25:
            mode = "anomaly"

        elif step <= 38:
            mode = "recovery"

        else:
            step = 0
            continue

        t = np.arange(
            samples
        ) / sample_rate

        if mode == "healthy":

            x = (
                0.15
                * np.sin(
                    2
                    * np.pi
                    * 8
                    * t
                )
                + np.random.normal(
                    0,
                    0.02,
                    samples,
                )
            )

            y = (
                0.08
                * np.sin(
                    2
                    * np.pi
                    * 8
                    * t
                )
                + np.random.normal(
                    0,
                    0.01,
                    samples,
                )
            )

            z = np.random.normal(
                0,
                0.02,
                samples,
            )

        elif mode == "anomaly":

            x = (
                0.75
                * np.sin(
                    2
                    * np.pi
                    * 28
                    * t
                )
                + np.random.normal(
                    0,
                    0.08,
                    samples,
                )
            )

            y = (
                0.45
                * np.sin(
                    2
                    * np.pi
                    * 28
                    * t
                )
                + np.random.normal(
                    0,
                    0.06,
                    samples,
                )
            )

            z = np.random.normal(
                0,
                0.1,
                samples,
            )

        else:

            decay = max(
                0.15,
                0.75
                - ((step - 25) * 0.045),
            )

            x = (
                decay
                * np.sin(
                    2
                    * np.pi
                    * 12
                    * t
                )
                + np.random.normal(
                    0,
                    0.04,
                    samples,
                )
            )

            y = (
                decay
                * 0.4
                * np.sin(
                    2
                    * np.pi
                    * 12
                    * t
                )
                + np.random.normal(
                    0,
                    0.03,
                    samples,
                )
            )

            z = np.random.normal(
                0,
                0.03,
                samples,
            )

        payload = {
            "machine_id": machine_id,
            "timestamp": time.time(),
            "sample_rate": sample_rate,
            "accelerometer": {
                "x": x.tolist(),
                "y": y.tolist(),
                "z": z.tolist(),
            },
        }

        response = await process_payload(
            machine_id,
            payload,
        )

        response["demo_mode"] = mode

        await websocket.send_json(
            response
        )

        await asyncio.sleep(1)