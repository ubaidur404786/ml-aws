"""Calls the language model. Bedrock in real mode, a free fake answer in mock mode."""
from app import config


# Example: mock_generate("...Context:\n[refund_policy.pdf p.1] Refunds within 30 days...\n\nQuestion: Refund window?")
#   -> {"answer": "[MOCK] Based on the context: Refunds within 30 days...", "input_tokens": 42, "output_tokens": 12}
#   A question that shares fewer than 2 words with the top chunk gets "[MOCK] I don't know".
def mock_generate(prompt: str) -> dict:
    context_lines = [line for line in prompt.splitlines() if line.startswith("[")]
    question = prompt.rsplit("Question:", 1)[-1].lower().replace("?", "").split()
    first_fact = context_lines[0].split("] ", 1)[1][:200] if context_lines else ""
    shared_words = set(question) & set(first_fact.lower().split()) - {"the", "a", "is", "to", "i", "do", "of"}
    answer = f"[MOCK] Based on the context: {first_fact}" if len(shared_words) >= 2 else "[MOCK] I don't know"
    return {"answer": answer, "input_tokens": len(prompt.split()), "output_tokens": len(answer.split())}


# Example: bedrock_generate("Answer ONLY from...", "amazon.nova-micro-v1:0", max_tokens=300)
#   -> {"answer": "Within 30 days with a receipt.", "input_tokens": 230, "output_tokens": 9}
def bedrock_generate(prompt: str, model_id: str, max_tokens: int) -> dict:
    import boto3  # imported here so mock mode works without AWS setup

    client = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)
    # Converse API: one request format that works for every Bedrock chat model
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0},
    )
    return {
        "answer": response["output"]["message"]["content"][0]["text"].strip(),
        "input_tokens": response["usage"]["inputTokens"],
        "output_tokens": response["usage"]["outputTokens"],
    }


# Example: generate("Answer ONLY from...", "amazon.nova-micro-v1:0")
#   -> {"answer": "...", "input_tokens": 230, "output_tokens": 9}
def generate(prompt: str, model_id: str, max_tokens: int = 300) -> dict:
    if config.LLM_MODE == "mock":
        return mock_generate(prompt)
    return bedrock_generate(prompt, model_id, max_tokens)
