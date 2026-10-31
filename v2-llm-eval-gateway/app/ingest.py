"""Build the search index. Run: python -m app.ingest

PDFs -> chunks -> embeddings -> FAISS index saved in index/
"""
import json

import faiss
import numpy as np

from app import config
from app.documents import load_chunks
from app.embeddings import embed


# Example: build_index() -> 6   (number of chunks; writes index/index.faiss and index/chunks.json)
def build_index() -> int:
    chunks = load_chunks(config.DOCS_DIR)
    if not chunks:
        raise SystemExit(f"No PDF text found in {config.DOCS_DIR}")
    vectors = np.array([embed(chunk["text"]) for chunk in chunks], dtype="float32")

    index = faiss.IndexFlatIP(config.EMBED_DIM)  # IP = inner product (= cosine, since vectors are unit length)
    index.add(vectors)

    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(config.INDEX_DIR / "index.faiss"))
    (config.INDEX_DIR / "chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    return len(chunks)


if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} chunks from {config.DOCS_DIR} ({config.LLM_MODE} embeddings) -> {config.INDEX_DIR}")
