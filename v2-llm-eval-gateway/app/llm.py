"""Calls the language model. In mock mode it returns a fake answer (free, no AWS)."""
from app import config


# Example: mock_generate("...Context:\n[policy.pdf p.2] Refunds within 30 days...")
#   -> {"answer": "[MOCK] Based on the context: Refunds within 30 days...", "input_tokens": 42, "output_tokens": 12}
def mock_generate(prompt: str) -> dict:
    context_lines = [line for line in prompt.splitlines() if line.startswith("[")]
    first_fact = context_lines[0].split("] ", 1)[1] if context_lines else "I don't know."
    answer = f"[MOCK] Based on the context: {first_fact}"
    return {"answer": answer, "input_tokens": len(prompt.split()), "output_tokens": len(answer.split())}


# Example: generate("Answer ONLY from...", "amazon.nova-micro-v1:0")
#   -> {"answer": "...", "input_tokens": 42, "output_tokens": 12}
def generate(prompt: str, model_id: str) -> dict:
    if config.LLM_MODE == "mock":
        return mock_generate(prompt)
    raise NotImplementedError("Bedrock mode is added in Step 2. Use LLM_MODE=mock for now.")
