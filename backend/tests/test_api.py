"""API endpoint integration tests using FastAPI TestClient."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_api_health_endpoints() -> None:
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"

    ready_res = client.get("/api/v1/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"


def test_api_sse_stream_endpoint() -> None:
    res = client.get("/api/v1/events/stream/00000000-0000-0000-0000-000000000001")
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
