"""LLM-as-judge: a separate model (NOT one of the candidates) scores each answer from 1 to 5.

Run: python -m eval.judge   (reads storage/eval_answers.json, writes storage/eval_judged.json)
"""
import json

from app import config, llm, storage
from eval import checks

RUBRIC = """You are grading an answer from a customer-support assistant.

Score each item from 1 (bad) to 5 (perfect):
- correctness: does the answer say the same thing as the expected answer?
  5 = same facts, 3 = partly right, 1 = wrong or missing.
- faithfulness: is every claim supported by the expected answer / documents, with nothing made up?
  5 = nothing invented, 1 = invents facts.
- refusal: if the expected answer is "I don't know", did the assistant refuse instead of guessing?
  5 = refused correctly (or the question was answerable and it did answer), 1 = guessed or wrongly refused.

Question: {question}
Expected answer: {expected_answer}
Assistant answer: {answer}

Reply with JSON only: {{"correctness": 1-5, "faithfulness": 1-5, "refusal": 1-5, "reason": "one short sentence"}}"""


# Example: mock_judge({"expected_answer": "3 to 5 business days.", "answer": "Standard shipping takes 3 to 5 business days.", ...})
#   -> {"correctness": 5, "faithfulness": 5, "refusal": 5, "reason": "[MOCK] word overlap 100%"}
def mock_judge(item: dict) -> dict:
    expected_unanswerable = checks.is_refusal(item["expected_answer"])
    if expected_unanswerable or checks.is_refusal(item["answer"]):
        score = 5 if expected_unanswerable == checks.is_refusal(item["answer"]) else 1
        return {"correctness": score, "faithfulness": 5, "refusal": score, "reason": "[MOCK] refusal check"}
    expected_words = set(item["expected_answer"].lower().replace(".", "").split())
    found = len(expected_words & set(item["answer"].lower().replace(".", "").split())) / len(expected_words)
    score = 5 if found >= 0.6 else 3 if found >= 0.3 else 1
    return {"correctness": score, "faithfulness": 4, "refusal": 5, "reason": f"[MOCK] word overlap {found:.0%}"}


# Example: parse_judge_reply('Sure! {"correctness": 4, "faithfulness": 5, "refusal": 5, "reason": "ok"}')
#   -> {"correctness": 4, "faithfulness": 5, "refusal": 5, "reason": "ok"}
def parse_judge_reply(reply: str) -> dict:
    scores = json.loads(reply[reply.find("{"): reply.rfind("}") + 1])  # ignore any text around the JSON
    for key in ("correctness", "faithfulness", "refusal"):
        scores[key] = max(1, min(5, int(scores[key])))  # clamp to 1..5
    return scores


# Example: judge_answer({"question": "...", "expected_answer": "...", "answer": "..."})
#   -> {"correctness": 5, "faithfulness": 5, "refusal": 5, "reason": "Same facts."}
def judge_answer(item: dict) -> dict:
    if config.LLM_MODE == "mock":
        return mock_judge(item)
    prompt = RUBRIC.format(question=item["question"], expected_answer=item["expected_answer"], answer=item["answer"])
    reply = llm.generate(prompt, config.JUDGE_MODEL, max_tokens=200)["answer"]
    try:
        return parse_judge_reply(reply)
    except (ValueError, KeyError):
        return {"correctness": 1, "faithfulness": 1, "refusal": 1, "reason": f"Judge reply not valid JSON: {reply[:100]}"}


# Example: judge_all([answer_item, ...]) -> [{...answer_item, "correctness": 5, ..., "right_source": True, "length_ok": True}, ...]
def judge_all(answers: list[dict]) -> list[dict]:
    if config.JUDGE_MODEL in config.CANDIDATE_MODELS:
        raise ValueError("The judge model must not be one of the candidate models")
    judged = []
    for item in answers:
        judged.append({
            **item,
            **judge_answer(item),
            "right_source": checks.right_source(item, item["sources"]),
            "length_ok": checks.length_ok(item["answer"]),
        })
    return judged


if __name__ == "__main__":
    judged_items = judge_all(storage.read_json("eval_answers.json", []))
    storage.write_json("eval_judged.json", judged_items)
    print(f"Judged {len(judged_items)} answers with {config.JUDGE_MODEL} ({config.LLM_MODE} mode)")
