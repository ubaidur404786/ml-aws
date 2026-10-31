"""FastAPI app. Run: uvicorn app.main:app --reload"""
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app import config, rag

app = FastAPI(title="LLM Eval & Gateway")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


# Example: GET /health -> {"status": "ok", "mode": "mock"}
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": config.LLM_MODE}


# Example: POST /ask {"question": "What is the refund window?"}
#   -> {"answer": "Within 30 days...", "sources": ["refund_policy.pdf p.1", ...], "model": "amazon.nova-micro-v1:0", ...}
@app.post("/ask")
def ask(request: AskRequest) -> dict:
    start = time.perf_counter()
    result = rag.answer_question(request.question, config.ACTIVE_MODEL)
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "model": config.ACTIVE_MODEL,
        "mode": config.LLM_MODE,
        "latency_ms": round((time.perf_counter() - start) * 1000),
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
    }
