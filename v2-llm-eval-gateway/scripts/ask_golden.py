"""Ask every golden question once and print the answers. Run: python scripts/ask_golden.py

Quick manual check of the RAG pipeline (the real evaluation comes in eval/).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so "app" can be imported

from app import config, rag  # noqa: E402


# Example: load_golden() -> [{"id": 1, "question": "How many days...", "expected_answer": "...", ...}, ...]
def load_golden() -> list[dict]:
    lines = (config.PROJECT_DIR / "data" / "golden.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


if __name__ == "__main__":
    total_in, total_out = 0, 0
    for row in load_golden():
        result = rag.answer_question(row["question"], config.ACTIVE_MODEL)
        total_in += result["input_tokens"]
        total_out += result["output_tokens"]
        print(f"#{row['id']} [{row['type']}] {row['question']}")
        print(f"   answer:   {result['answer']}")
        print(f"   expected: {row['expected_answer']}")
        print(f"   sources:  {', '.join(result['sources'])}  (expected: {row['source'] or 'none'})")
        print(f"   tokens:   {result['input_tokens']} in / {result['output_tokens']} out\n")
    print(f"Model {config.ACTIVE_MODEL} ({config.LLM_MODE}): {total_in} input + {total_out} output tokens in total")
