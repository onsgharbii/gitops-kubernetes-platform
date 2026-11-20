"""API gateway: the single public entry point in front of the inference service."""
import os

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, make_asgi_app
from pydantic import BaseModel

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://inference:8000")
APP_VERSION = os.getenv("APP_VERSION", "dev")

REQUESTS = Counter("api_requests_total", "API requests", ["endpoint", "status"])

app = FastAPI(title="api")
app.mount("/metrics", make_asgi_app())


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/info")
def info():
    REQUESTS.labels(endpoint="info", status="200").inc()
    return {"service": "api", "version": APP_VERSION}


@app.post("/api/predict")
def predict(req: PredictRequest):
    try:
        resp = httpx.post(f"{INFERENCE_URL}/predict", json=req.model_dump(), timeout=5)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        REQUESTS.labels(endpoint="predict", status="502").inc()
        raise HTTPException(status_code=502, detail="inference service unavailable") from exc
    REQUESTS.labels(endpoint="predict", status="200").inc()
    return resp.json()
