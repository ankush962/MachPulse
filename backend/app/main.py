from fastapi import FastAPI

app = FastAPI(
    title="MachPulse API",
    version="0.1.0",
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