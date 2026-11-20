from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_predict_positive():
    body = client.post("/predict", json={"text": "great and reliable"}).json()
    assert body["label"] == "positive"
    assert body["score"] == 2


def test_predict_negative():
    assert client.post("/predict", json={"text": "slow"}).json()["label"] == "negative"


def test_predict_neutral():
    assert client.post("/predict", json={"text": "hello"}).json()["label"] == "neutral"


def test_metrics_exposed():
    client.post("/predict", json={"text": "good"})
    assert "inference_predictions_total" in client.get("/metrics/").text
