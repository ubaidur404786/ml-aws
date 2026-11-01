"""Turn judged answers into a leaderboard: CSV + Markdown table + PNG charts.

Run: python -m eval.report   (reads storage/eval_judged.json, writes eval/results/)
Recommended model = cheapest, then fastest, among models with correctness >= 85% and refusal >= 90%.
"""
import csv
from pathlib import Path

from app import config, storage

MIN_CORRECTNESS_PCT = 85
MIN_REFUSAL_PCT = 90
PASS_SCORE = 4  # a judge score of 4 or 5 counts as "passed"
RESULTS_DIR = config.PROJECT_DIR / "eval" / "results"


# Example: percentile([100, 200, 300, 400], 50) -> 200
def percentile(values: list[float], pct: int) -> float:
    ordered = sorted(values)
    index = max(0, round(pct / 100 * len(ordered)) - 1)
    return ordered[index]


# Example: pass_rate([{"correctness": 5}, {"correctness": 2}], "correctness") -> 50.0
#          pass_rate([], "refusal") -> 100.0   (nothing to fail)
def pass_rate(items: list[dict], key: str) -> float:
    if not items:
        return 100.0
    return round(100 * sum(item[key] >= PASS_SCORE for item in items) / len(items), 1)


# Example: summarize_model("amazon.nova-micro-v1:0", [judged items for that model])
#   -> {"model": "amazon.nova-micro-v1:0", "correctness_pct": 87.5, "faithfulness_avg": 4.6, "refusal_pct": 100.0,
#       "p50_latency_ms": 610, "p95_latency_ms": 900, "cost_per_1000_usd": 0.09, "right_source_pct": 90.0, ...}
def summarize_model(model_id: str, items: list[dict]) -> dict:
    answerable = [item for item in items if item["type"] != "unanswerable"]
    unanswerable = [item for item in items if item["type"] == "unanswerable"]
    latencies = [item["latency_ms"] for item in items]
    return {
        "model": model_id,
        "questions": len(items),
        "correctness_pct": pass_rate(answerable, "correctness"),
        "faithfulness_avg": round(sum(item["faithfulness"] for item in items) / len(items), 2),
        "refusal_pct": pass_rate(unanswerable, "refusal"),
        "right_source_pct": round(100 * sum(item["right_source"] for item in items) / len(items), 1),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "cost_per_1000_usd": round(1000 * sum(item["cost_usd"] for item in items) / len(items), 4),
    }


# Example: build_leaderboard([judged items of all models]) -> [summary_for_micro, summary_for_lite, ...]
def build_leaderboard(judged: list[dict]) -> list[dict]:
    model_ids = list(dict.fromkeys(item["model"] for item in judged))  # keep first-seen order
    return [summarize_model(model_id, [i for i in judged if i["model"] == model_id]) for model_id in model_ids]


# Example: recommend([{"model": "micro", "correctness_pct": 90, "refusal_pct": 100, "cost_per_1000_usd": 0.1, ...}, ...])
#   -> "micro"   (or None if no model passes both thresholds)
def recommend(leaderboard: list[dict]) -> str | None:
    passing = [row for row in leaderboard
               if row["correctness_pct"] >= MIN_CORRECTNESS_PCT and row["refusal_pct"] >= MIN_REFUSAL_PCT]
    if not passing:
        return None
    best = min(passing, key=lambda row: (row["cost_per_1000_usd"], row["p50_latency_ms"]))
    return best["model"]


# Example: write_csv(leaderboard, Path("eval/results/leaderboard.csv")) -> creates the CSV file
def write_csv(leaderboard: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(leaderboard[0]))
        writer.writeheader()
        writer.writerows(leaderboard)


# Example: markdown_table(leaderboard, "amazon.nova-micro-v1:0")
#   -> "| Model | Correctness | ... |\n|---|...\n| ✅ amazon.nova-micro-v1:0 | 90.0% | ... |"
def markdown_table(leaderboard: list[dict], recommended: str | None) -> str:
    lines = [
        "| Model | Correctness | Faithfulness | Refusal | Right source | p50 ms | p95 ms | $ / 1000 questions |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in leaderboard:
        mark = "✅ " if row["model"] == recommended else ""
        lines.append(
            f"| {mark}{row['model']} | {row['correctness_pct']}% | {row['faithfulness_avg']} | {row['refusal_pct']}% "
            f"| {row['right_source_pct']}% | {row['p50_latency_ms']} | {row['p95_latency_ms']} | ${row['cost_per_1000_usd']} |"
        )
    lines.append(f"\nRecommended: **{recommended or 'none (no model passes the thresholds)'}**")
    return "\n".join(lines)


# Example: draw_charts(leaderboard, Path("eval/results")) -> creates quality_vs_cost.png and latency.png
def draw_charts(leaderboard: list[dict], folder: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")  # draw to files, no window
    import matplotlib.pyplot as plt

    names = [row["model"].replace("amazon.", "").replace("-v1:0", "") for row in leaderboard]

    plt.figure(figsize=(6, 4))
    plt.scatter([row["cost_per_1000_usd"] for row in leaderboard], [row["correctness_pct"] for row in leaderboard])
    for name, row in zip(names, leaderboard):
        plt.annotate(name, (row["cost_per_1000_usd"], row["correctness_pct"]))
    plt.axhline(MIN_CORRECTNESS_PCT, linestyle="--", color="gray")  # pass line
    plt.xlabel("$ per 1000 questions")
    plt.ylabel("Correctness %")
    plt.title("Quality vs cost")
    plt.tight_layout()
    plt.savefig(folder / "quality_vs_cost.png")
    plt.close()

    plt.figure(figsize=(6, 4))
    positions = range(len(names))
    plt.bar([p - 0.2 for p in positions], [row["p50_latency_ms"] for row in leaderboard], width=0.4, label="p50")
    plt.bar([p + 0.2 for p in positions], [row["p95_latency_ms"] for row in leaderboard], width=0.4, label="p95")
    plt.xticks(list(positions), names)
    plt.ylabel("Latency (ms)")
    plt.title("Latency per model")
    plt.legend()
    plt.tight_layout()
    plt.savefig(folder / "latency.png")
    plt.close()


# Example: make_report([judged items]) -> {"leaderboard": [...], "recommended": "amazon.nova-micro-v1:0", "mode": "mock"}
#   (also saves storage/eval_report.json for the admin dashboard)
def make_report(judged: list[dict]) -> dict:
    leaderboard = build_leaderboard(judged)
    report = {"leaderboard": leaderboard, "recommended": recommend(leaderboard), "mode": config.LLM_MODE}
    storage.write_json("eval_report.json", report)
    return report


if __name__ == "__main__":
    result = make_report(storage.read_json("eval_judged.json", []))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(result["leaderboard"], RESULTS_DIR / "leaderboard.csv")
    table = markdown_table(result["leaderboard"], result["recommended"])
    (RESULTS_DIR / "leaderboard.md").write_text(table + "\n", encoding="utf-8")
    draw_charts(result["leaderboard"], RESULTS_DIR)
    print(table)
    print(f"\nWrote leaderboard.csv, leaderboard.md, quality_vs_cost.png, latency.png to {RESULTS_DIR}")
