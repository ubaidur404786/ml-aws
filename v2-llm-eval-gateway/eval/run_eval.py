"""The whole evaluation in one call: run models -> judge -> report.

Used by the admin dashboard ("Run evaluation") and by: python -m eval.run_eval --sample 5
"""
import argparse
from datetime import datetime

from app import config, storage
from eval.judge import judge_all
from eval.report import make_report
from eval.run_models import load_golden, run_models


# Example: run_eval(["amazon.nova-micro-v1:0", "amazon.nova-lite-v1:0"], sample_size=5)
#   -> {"run_id": "2026-11-01T10-00-00", "leaderboard": [...], "recommended": "amazon.nova-micro-v1:0", "mode": "mock"}
def run_eval(model_ids: list[str], sample_size: int | None = None) -> dict:
    answers = run_models(model_ids, load_golden(sample_size))
    judged = judge_all(answers)
    storage.write_json("eval_judged.json", judged)
    report = make_report(judged)
    report["run_id"] = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    storage.write_json("eval_report.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="only use the first N golden rows")
    args = parser.parse_args()
    summary = run_eval(config.CANDIDATE_MODELS, args.sample)
    for row in summary["leaderboard"]:
        print(row)
    print(f"Recommended: {summary['recommended']}")
