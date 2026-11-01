from app import pricing
from eval import checks
from eval.human_check import agreement_pct
from eval.judge import mock_judge, parse_judge_reply
from eval.report import build_leaderboard, percentile, recommend


def make_item(model, row_id, row_type, correctness, refusal, latency, cost):
    return {"model": model, "id": row_id, "type": row_type, "correctness": correctness, "faithfulness": 5,
            "refusal": refusal, "right_source": True, "latency_ms": latency, "cost_usd": cost}


def test_cost_usd():
    assert round(pricing.cost_usd("amazon.nova-lite-v1:0", 1000, 500), 6) == 0.00018


def test_checks():
    assert checks.is_refusal("I don't know")
    assert not checks.is_refusal("3 to 5 business days.")
    assert checks.right_source({"source": "a.pdf p.1; a.pdf p.2"}, ["a.pdf p.2", "a.pdf p.1"])
    assert not checks.right_source({"source": "a.pdf p.1"}, ["b.pdf p.1"])
    assert checks.length_ok("short answer") and not checks.length_ok("word " * 200)


def test_parse_judge_reply_clamps_scores():
    scores = parse_judge_reply('Here: {"correctness": 9, "faithfulness": 0, "refusal": 5, "reason": "x"}')
    assert (scores["correctness"], scores["faithfulness"], scores["refusal"]) == (5, 1, 5)


def test_mock_judge_rewards_correct_refusal():
    assert mock_judge({"expected_answer": "I don't know", "answer": "[MOCK] I don't know"})["refusal"] == 5
    assert mock_judge({"expected_answer": "I don't know", "answer": "It is in Paris."})["refusal"] == 1


def test_percentile():
    assert percentile([100, 200, 300, 400], 50) == 200
    assert percentile([100, 200, 300, 400], 95) == 400


def test_recommend_picks_cheapest_passing_model():
    judged = []
    for model, correctness, cost in [("good-cheap", 5, 0.001), ("good-expensive", 5, 0.01), ("bad-cheapest", 2, 0.0001)]:
        judged.append(make_item(model, 1, "easy", correctness, 5, 500, cost))
        judged.append(make_item(model, 2, "unanswerable", 5, 5, 500, cost))
    assert recommend(build_leaderboard(judged)) == "good-cheap"


def test_recommend_none_when_nobody_passes():
    judged = [make_item("m", 1, "easy", 2, 5, 500, 0.001)]
    assert recommend(build_leaderboard(judged)) is None


def test_agreement_pct():
    assert agreement_pct([{"judge": 5, "human": 4}, {"judge": 5, "human": 2}]) == 50.0
