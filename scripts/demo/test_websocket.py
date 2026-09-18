from __future__ import annotations

import asyncio
import json

import websockets


async def main() -> None:

    uri = (
        "ws://localhost:8000"
        "/ws/demo/M01"
    )

    async with websockets.connect(
        uri
    ) as websocket:

        for _ in range(5):

            message = await websocket.recv()

            data = json.loads(
                message
            )

            print(
                json.dumps(
                    data,
                    indent=2,
                )
            )


if __name__ == "__main__":
    asyncio.run(main())