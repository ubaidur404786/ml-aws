"""Ask every golden question to every candidate model with the SAME RAG pipeline.

Run: python -m eval.run_models            (all rows, all candidate models)
     python -m eval.run_models --sample 3 (first 3 rows only)
Writes storage/eval_answers.json
"""
import argparse
import json
import time

from app import config, pricing, rag, storage


# Example: load_golden(sample_size=2) -> [{"id": 1, "question": "...", "expected_answer": "...", ...}, {...}]
def load_golden(sample_size: int | None = None) -> list[dict]:
    lines = config.GOLDEN_FILE.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return rows[:sample_size] if sample_size else rows


# Example: ask_one_model("amazon.nova-lite-v1:0", {"id": 3, "question": "How long does standard shipping take?", ...})
#   -> {"id": 3, "model": "amazon.nova-lite-v1:0", "answer": "3 to 5 business days.", "sources": [...],
#       "latency_ms": 640, "input_tokens": 230, "output_tokens": 9, "cost_usd": 0.0000159, ...}
def ask_one_model(model_id: str, row: dict) -> dict:
    start = time.perf_counter()
    result = rag.answer_question(row["question"], model_id)
    latency_ms = round((time.perf_counter() - start) * 1000)
    return {
        **row,  # keep question, expected answer, source and type next to the answer
        "model": model_id,
        "answer": result["answer"],
        "sources": result["sources"],
        "latency_ms": latency_ms,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": pricing.cost_usd(model_id, result["input_tokens"], result["output_tokens"]),
    }


# Example: run_models(["amazon.nova-micro-v1:0"], [row1, row2]) -> [answer_for_row1, answer_for_row2]
def run_models(model_ids: list[str], rows: list[dict]) -> list[dict]:
    return [ask_one_model(model_id, row) for model_id in model_ids for row in rows]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="only use the first N golden rows")
    args = parser.parse_args()

    answers = run_models(config.CANDIDATE_MODELS, load_golden(args.sample))
    storage.write_json("eval_answers.json", answers)
    print(f"Saved {len(answers)} answers from {len(config.CANDIDATE_MODELS)} models ({config.LLM_MODE} mode)")
