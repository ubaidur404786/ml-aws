"""Retrieval. Step 1 uses a tiny in-memory list; Step 2 replaces it with Titan embeddings + FAISS."""

SAMPLE_CHUNKS = [
    {"text": "Refunds are accepted within 30 days of purchase with a receipt.", "source": "policy.pdf p.2"},
    {"text": "Support is available Monday to Friday, 9:00 to 17:00.", "source": "policy.pdf p.4"},
    {"text": "Standard shipping takes 3 to 5 business days.", "source": "shipping.pdf p.1"},
]


# Example: count_shared_words("refund window?", "Refunds are accepted...") -> 0 or more
def count_shared_words(question: str, text: str) -> int:
    question_words = set(question.lower().replace("?", "").split())
    text_words = set(text.lower().replace(".", "").replace(",", "").split())
    return len(question_words & text_words)


# Example: retrieve("How long does shipping take?", k=1)
#   -> [{"text": "Standard shipping takes 3 to 5 business days.", "source": "shipping.pdf p.1"}]
def retrieve(question: str, k: int = 2) -> list[dict]:
    ranked = sorted(SAMPLE_CHUNKS, key=lambda chunk: count_shared_words(question, chunk["text"]), reverse=True)
    return ranked[:k]


# Example: build_prompt("Refund window?", [{"text": "Refunds within 30 days", "source": "policy.pdf p.2"}])
#   -> "Answer ONLY from the context below...\n[policy.pdf p.2] Refunds within 30 days\n\nQuestion: Refund window?"
def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n".join(f"[{chunk['source']}] {chunk['text']}" for chunk in chunks)
    return (
        "Answer ONLY from the context below. If the answer is not in the context, say \"I don't know\".\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
