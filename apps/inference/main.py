"""Toy sentiment "model" served over HTTP.

The model itself is deliberately trivial: the point of this repository is the
delivery platform around it (CI/CD, GitOps, Blue/Green, observability).
"""
import os

from fastapi import FastAPI
from prometheus_client import Counter, make_asgi_app
from pydantic import BaseModel

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
DEPLOYMENT_COLOR = os.getenv("DEPLOYMENT_COLOR", "blue")

POSITIVE = {"good", "great", "excellent", "love", "happy", "fast", "reliable"}
NEGATIVE = {"bad", "terrible", "hate", "slow", "broken", "angry", "down"}

PREDICTIONS = Counter(
    "inference_predictions_total", "Predictions served", ["label", "model_version"]
)

app = FastAPI(title="inference")
app.mount("/metrics", make_asgi_app())


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    words = req.text.lower().split()
    score = sum(w in POSITIVE for w in words) - sum(w in NEGATIVE for w in words)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    PREDICTIONS.labels(label=label, model_version=MODEL_VERSION).inc()
    return {
        "label": label,
        "score": score,
        "model_version": MODEL_VERSION,
        "color": DEPLOYMENT_COLOR,
    }
