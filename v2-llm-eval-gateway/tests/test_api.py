from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_returns_answer_and_sources():
    response = client.post("/ask", json={"question": "When are refunds accepted?"})
    body = response.json()
    assert response.status_code == 200
    assert body["answer"].startswith("[MOCK]")
    assert body["sources"][0] == "policy.pdf p.2"


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
