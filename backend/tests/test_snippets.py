def test_snippet_round_trip(client, monkeypatch, tmp_path) -> None:
    from app.services import snippet_store

    monkeypatch.setattr(snippet_store, "DB_PATH", tmp_path / "snippets.db")
    created = client.post("/api/snippets", json={"code": "int main() { return 0; }"})
    assert created.status_code == 201
    snippet_id = created.json()["id"]
    loaded = client.get(f"/api/snippets/{snippet_id}")
    assert loaded.status_code == 200
    assert loaded.json()["code"] == "int main() { return 0; }"
    assert loaded.json()["trace"]["success"] is True
