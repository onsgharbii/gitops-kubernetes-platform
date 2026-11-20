import httpx
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_info():
    assert client.get("/api/info").json()["service"] == "api"


def test_predict_forwards_to_inference(monkeypatch):
    def fake_post(url, json, timeout):
        assert url.endswith("/predict")
        return httpx.Response(200, json={"label": "positive"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(main.httpx, "post", fake_post)
    assert client.post("/api/predict", json={"text": "good"}).json() == {"label": "positive"}


def test_predict_returns_502_when_inference_down(monkeypatch):
    def failing_post(url, json, timeout):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(main.httpx, "post", failing_post)
    assert client.post("/api/predict", json={"text": "good"}).status_code == 502
