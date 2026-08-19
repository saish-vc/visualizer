from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_trace_simple_program() -> None:
    response = client.post("/api/trace", json={"code": "int main() { int x = 2; x += 3; return x; }"})
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["steps"]


def test_compile_error_is_structured_response() -> None:
    body = client.post("/api/trace", json={"code": "int main( {"}).json()
    assert body["success"] is False
    assert body["compile_error"]
    assert body["steps"] == []


def test_infinite_loop_is_truncated() -> None:
    body = client.post("/api/trace", json={"code": "int main() { while (true) {} }"}).json()
    assert body["success"] is True
    assert body["truncated"] is True
