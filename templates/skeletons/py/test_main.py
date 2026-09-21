from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_exemplo():
    assert client.get("/api/exemplo").status_code == 200
