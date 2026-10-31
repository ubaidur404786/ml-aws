"""Draft golden questions from your PDFs. Run: python scripts/draft_golden.py

Writes data/golden_draft.jsonl. These are only DRAFTS: review every row by hand
(fix the question, the expected answer and the source), then copy the good rows into data/golden.jsonl.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so "app" can be imported

from app import config, llm  # noqa: E402
from app.documents import load_chunks  # noqa: E402

DRAFT_FILE = config.PROJECT_DIR / "data" / "golden_draft.jsonl"

DRAFT_PROMPT = (
    "Write ONE question a customer could ask that is answered by the text below, "
    "then the short correct answer. Reply as JSON: {{\"question\": \"...\", \"expected_answer\": \"...\"}}\n\n"
    "Text:\n{text}"
)


# Example: draft_row(1, {"text": "Refunds within 30 days...", "source": "refund_policy.pdf p.1"})
#   -> {"id": 1, "question": "How long is the refund window?", "expected_answer": "30 days",
#       "source": "refund_policy.pdf p.1", "type": "easy"}
def draft_row(row_id: int, chunk: dict) -> dict:
    reply = llm.generate(DRAFT_PROMPT.format(text=chunk["text"]), config.ACTIVE_MODEL)["answer"]
    try:
        parsed = json.loads(reply[reply.find("{"): reply.rfind("}") + 1])
    except json.JSONDecodeError:
        parsed = {"question": "TODO: write question", "expected_answer": reply}  # mock mode lands here
    return {
        "id": row_id,
        "question": parsed.get("question", ""),
        "expected_answer": parsed.get("expected_answer", ""),
        "source": chunk["source"],
        "type": "easy",
    }


if __name__ == "__main__":
    chunks = load_chunks(config.DOCS_DIR)
    rows = [draft_row(row_id, chunk) for row_id, chunk in enumerate(chunks, start=1)]
    DRAFT_FILE.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} draft rows to {DRAFT_FILE}. Review every row by hand before using it.")
