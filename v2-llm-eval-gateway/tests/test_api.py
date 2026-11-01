import json

import pytest
from fastapi.testclient import TestClient

from app import config, rag
from app.documents import split_into_chunks
from app.ingest import build_index
from app.main import app

client = TestClient(app)
ADMIN = {"X-Admin-Password": "test-password"}


@pytest.fixture(autouse=True, scope="module")
def mock_setup(tmp_path_factory):
    # Mock mode, a fresh index of the sample PDFs and an empty storage folder: free and offline.
    config.LLM_MODE = "mock"
    config.ADMIN_PASSWORD = "test-password"
    config.INDEX_DIR = tmp_path_factory.mktemp("index")
    config.STORAGE_DIR = tmp_path_factory.mktemp("storage")
    rag.load_index.cache_clear()
    build_index()
    yield
    rag.load_index.cache_clear()


def test_split_into_chunks_overlaps():
    assert split_into_chunks("one two three four five", chunk_words=3, overlap_words=1) == [
        "one two three",
        "three four five",
    ]


def test_retrieve_finds_shipping_page():
    top = rag.retrieve("How much does express shipping cost?", k=1)[0]
    assert top["source"] == "shipping_guide.pdf p.1"


def test_golden_rows_have_required_fields():
    lines = config.GOLDEN_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        row = json.loads(line)
        assert set(row) == {"id", "question", "expected_answer", "source", "type"}
        assert row["type"] in {"easy", "multi", "unanswerable"}


def test_pages_are_served_or_explain_how_to_build():
    # 200 when frontend/dist exists (after npm run build), otherwise 503 with the build command
    for path in ("/", "/admin"):
        response = client.get(path)
        assert response.status_code == 200 or "npm run build" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_returns_answer_sources_and_model():
    response = client.post("/ask", json={"question": "When is customer support open?"})
    body = response.json()
    assert response.status_code == 200
    assert body["answer"].startswith("[MOCK]")
    assert body["sources"][0] == "support_handbook.pdf p.1"
    assert body["model"] == "amazon.nova-micro-v1:0"


def test_ask_rejects_empty_question():
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_admin_needs_password():
    assert client.get("/admin/settings").status_code == 401
    assert client.get("/admin/settings", headers={"X-Admin-Password": "wrong"}).status_code == 401


def test_admin_eval_returns_leaderboard():
    response = client.post("/admin/eval", headers=ADMIN, json={"models": ["amazon.nova-micro-v1:0"], "sample_size": 3})
    body = response.json()
    assert response.status_code == 200
    assert body["leaderboard"][0]["model"] == "amazon.nova-micro-v1:0"
    assert len(client.get("/admin/results", headers=ADMIN).json()["answers"]) == 3


def test_admin_eval_rejects_unknown_model():
    response = client.post("/admin/eval", headers=ADMIN, json={"models": ["gpt-x"], "sample_size": 1})
    assert response.status_code == 400


def test_settings_change_model_and_daily_limit():
    new_settings = {"active_model": "amazon.nova-lite-v1:0", "allowed_models": ["amazon.nova-lite-v1:0"],
                    "max_tokens": 200, "daily_question_limit": 0}
    assert client.put("/admin/settings", headers=ADMIN, json=new_settings).status_code == 200
    assert client.post("/ask", json={"question": "Shipping time?"}).status_code == 429  # limit 0 = blocked

    new_settings["daily_question_limit"] = 100
    client.put("/admin/settings", headers=ADMIN, json=new_settings)
    assert client.post("/ask", json={"question": "Shipping time?"}).json()["model"] == "amazon.nova-lite-v1:0"


def test_settings_reject_active_model_not_allowed():
    bad = {"active_model": "amazon.nova-pro-v1:0", "allowed_models": ["amazon.nova-lite-v1:0"],
           "max_tokens": 200, "daily_question_limit": 10}
    assert client.put("/admin/settings", headers=ADMIN, json=bad).status_code == 400


def test_usage_counts_questions():
    usage = client.get("/admin/usage", headers=ADMIN).json()
    assert usage["today"]["questions"] >= 2
