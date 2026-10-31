import json

import pytest
from fastapi.testclient import TestClient

from app import config, rag
from app.documents import split_into_chunks
from app.ingest import build_index
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def mock_index(tmp_path_factory):
    # Build a mock-mode index of the sample PDFs in a temp folder, so tests are free and offline.
    config.LLM_MODE = "mock"
    config.INDEX_DIR = tmp_path_factory.mktemp("index")
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
    lines = (config.PROJECT_DIR / "data" / "golden.jsonl").read_text(encoding="utf-8").splitlines()
    for line in lines:
        row = json.loads(line)
        assert set(row) == {"id", "question", "expected_answer", "source", "type"}
        assert row["type"] in {"easy", "multi", "unanswerable"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_returns_answer_and_sources():
    response = client.post("/ask", json={"question": "When is customer support open?"})
    body = response.json()
    assert response.status_code == 200
    assert body["answer"].startswith("[MOCK]")
    assert body["sources"][0] == "support_handbook.pdf p.1"


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
