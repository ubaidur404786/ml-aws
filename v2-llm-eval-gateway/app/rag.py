"""Retrieval: find the chunks most similar to the question, then ask the model."""
import json
from functools import lru_cache

import faiss
import numpy as np

from app import config, llm
from app.embeddings import embed


# Example: load_index() -> (<faiss index with 6 vectors>, [{"text": "...", "source": "refund_policy.pdf p.1"}, ...])
@lru_cache(maxsize=1)
def load_index() -> tuple:
    index_file = config.INDEX_DIR / "index.faiss"
    if not index_file.exists():
        raise FileNotFoundError(f"{index_file} not found. Run: python -m app.ingest")
    chunks = json.loads((config.INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))
    return faiss.read_index(str(index_file)), chunks


# Example: retrieve("What is the refund window?", k=2)
#   -> [{"text": "Refunds are accepted within 30 days...", "source": "refund_policy.pdf p.1", "score": 0.61}, ...]
def retrieve(question: str, k: int = 3) -> list[dict]:
    index, chunks = load_index()
    query = np.array([embed(question)], dtype="float32")
    scores, positions = index.search(query, min(k, len(chunks)))
    return [{**chunks[pos], "score": round(float(score), 3)} for score, pos in zip(scores[0], positions[0])]


# Example: build_prompt("Refund window?", [{"text": "Refunds within 30 days", "source": "refund_policy.pdf p.1"}])
#   -> "Answer ONLY from the context below...\n[refund_policy.pdf p.1] Refunds within 30 days\n\nQuestion: Refund window?"
def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n".join(f"[{chunk['source']}] {chunk['text']}" for chunk in chunks)
    return (
        "Answer ONLY from the context below. If the answer is not in the context, reply exactly \"I don't know\".\n"
        "Keep the answer short (1-3 sentences).\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )


# Example: answer_question("What is the refund window?", "amazon.nova-micro-v1:0")
#   -> {"answer": "Within 30 days with a receipt.", "sources": ["refund_policy.pdf p.1", ...],
#       "input_tokens": 230, "output_tokens": 9}
def answer_question(question: str, model_id: str, max_tokens: int = 300, k: int = 3) -> dict:
    chunks = retrieve(question, k)
    result = llm.generate(build_prompt(question, chunks), model_id, max_tokens)
    return {**result, "sources": [chunk["source"] for chunk in chunks]}
