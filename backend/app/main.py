from fastapi import FastAPI

from backend.app.api.websocket import (
    router as websocket_router,
)


app = FastAPI(
    title="MachPulse API",
    version="0.1.0",
)


app.include_router(
    websocket_router
)


@app.get("/")
def root():

    return {
        "project": "MachPulse",
        "status": "running",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
    }