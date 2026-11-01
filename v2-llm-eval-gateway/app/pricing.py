"""Bedrock on-demand prices in USD per 1,000 tokens (us-east-1).

Checked 2026-10-31 with the AWS Price List API. Rows marked "not confirmed" were missing from
that query: re-check them on https://aws.amazon.com/bedrock/pricing/ before trusting cost numbers.
"""

PRICES_PER_1K = {
    "amazon.nova-micro-v1:0": {"input": 0.000035, "output": 0.00014},  # input not confirmed
    "amazon.nova-lite-v1:0": {"input": 0.00006, "output": 0.00024},
    "amazon.nova-pro-v1:0": {"input": 0.0008, "output": 0.0032},
    "amazon.nova-premier-v1:0": {"input": 0.0025, "output": 0.0125},  # not confirmed
}


# Example: cost_usd("amazon.nova-lite-v1:0", input_tokens=1000, output_tokens=500) -> 0.00018
def cost_usd(model_id: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICES_PER_1K.get(model_id, {"input": 0.0, "output": 0.0})  # unknown model -> 0, shown as $0
    return input_tokens / 1000 * price["input"] + output_tokens / 1000 * price["output"]
