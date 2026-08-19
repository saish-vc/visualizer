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


def test_program_with_output_completes_and_reports_stdout() -> None:
    code = '#include <iostream>\n\nint twice(int n) {\n  return n * 2;\n}\n\nint main() {\n  int value = twice(3);\n  std::cout << value << "\\n";\n  return 0;\n}\n'
    body = client.post("/api/trace", json={"code": code}).json()
    assert body["success"] is True
    assert body["truncated"] is False
    assert body["final_stdout"] == "6\n"
    assert "".join(step["stdout_delta"] for step in body["steps"]) == "6\n"
    assert any(step["locals"].get("n") == "3" for step in body["steps"])


def test_infinite_loop_is_truncated() -> None:
    body = client.post("/api/trace", json={"code": "int main() { while (true) {} }"}).json()
    assert body["success"] is True
    assert body["truncated"] is True
