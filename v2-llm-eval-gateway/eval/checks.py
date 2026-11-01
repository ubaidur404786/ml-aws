"""Simple rule-based checks that need no LLM."""


# Example: is_refusal("I don't know") -> True
#          is_refusal("Refunds within 30 days.") -> False
def is_refusal(answer: str) -> bool:
    return "don't know" in answer.lower() or "do not know" in answer.lower()


# Example: right_source({"source": "shipping_guide.pdf p.1", ...}, ["shipping_guide.pdf p.1", "refund_policy.pdf p.2"]) -> True
#          right_source({"source": "", ...}, [...]) -> True   (unanswerable rows have no expected source)
def right_source(row: dict, sources: list[str]) -> bool:
    expected = [source.strip() for source in row["source"].split(";") if source.strip()]
    return all(source in sources for source in expected)


# Example: length_ok("3 to 5 business days.") -> True
#          length_ok("word " * 200) -> False
def length_ok(answer: str, max_words: int = 80) -> bool:
    return 0 < len(answer.split()) <= max_words
