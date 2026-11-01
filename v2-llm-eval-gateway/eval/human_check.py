"""Check the judge: YOU score 20 answers, then see how often the judge agrees with you.

Run: python -m eval.human_check
For each answer type a correctness score 1-5 (or Enter to skip). Scores are saved to
storage/human_scores.json, so you can stop and continue later.
"""
from app import storage
from eval.report import PASS_SCORE

HOW_MANY = 20


# Example: agreement_pct([{"judge": 5, "human": 4}, {"judge": 5, "human": 2}]) -> 50.0
#   Judge and human "agree" when both say pass (>= 4) or both say fail (< 4).
def agreement_pct(pairs: list[dict]) -> float:
    if not pairs:
        return 0.0
    agreed = sum((pair["judge"] >= PASS_SCORE) == (pair["human"] >= PASS_SCORE) for pair in pairs)
    return round(100 * agreed / len(pairs), 1)


# Example: ask_score() -> 4   (after the user types "4"), or None after pressing Enter
def ask_score() -> int | None:
    while True:
        typed = input("   Your correctness score 1-5 (Enter = skip): ").strip()
        if typed == "":
            return None
        if typed in {"1", "2", "3", "4", "5"}:
            return int(typed)
        print("   Please type a number from 1 to 5.")


if __name__ == "__main__":
    judged = storage.read_json("eval_judged.json", [])[:HOW_MANY]
    human_scores = storage.read_json("human_scores.json", {})  # key: "model|id" -> score

    for item in judged:
        key = f"{item['model']}|{item['id']}"
        if key in human_scores:
            continue
        print(f"\n[{item['model']}] {item['question']}")
        print(f"   expected: {item['expected_answer']}")
        print(f"   answer:   {item['answer']}")
        score = ask_score()
        if score is not None:
            human_scores[key] = score
            storage.write_json("human_scores.json", human_scores)

    pairs = [{"judge": item["correctness"], "human": human_scores[f"{item['model']}|{item['id']}"]}
             for item in judged if f"{item['model']}|{item['id']}" in human_scores]
    result = {"scored": len(pairs), "agreement_pct": agreement_pct(pairs)}
    storage.write_json("judge_agreement.json", result)
    print(f"\nJudge agrees with you on {result['agreement_pct']}% of {result['scored']} answers.")
