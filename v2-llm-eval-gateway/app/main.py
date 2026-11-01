"""FastAPI app. Run: uvicorn app.main:app --reload

Client:  GET /  (chat page)        POST /ask
Admin:   GET /admin (dashboard)    /admin/* API, needs header X-Admin-Password
"""
import secrets
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import config, pricing, rag, settings, storage
from eval.run_eval import run_eval

FRONTEND_DIST = config.PROJECT_DIR / "frontend" / "dist"  # React build output (cd frontend && npm run build)
MAX_EVAL_SAMPLE = 10  # the dashboard only runs small, cheap evaluations

app = FastAPI(title="LLM Eval & Gateway")
# check_dir=False: the server can start before the first build; files are looked up per request
app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets", check_dir=False), name="assets")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class EvalRequest(BaseModel):
    models: list[str] = Field(min_length=1)
    sample_size: int = Field(default=5, ge=1, le=MAX_EVAL_SAMPLE)


class SettingsRequest(BaseModel):
    active_model: str
    allowed_models: list[str] = Field(min_length=1)
    max_tokens: int = Field(ge=50, le=2000)
    daily_question_limit: int = Field(ge=0, le=100000)


# Example: check_admin("correct-password") -> None;  check_admin("wrong") -> HTTP 401
def check_admin(x_admin_password: str = Header(default="")) -> None:
    if not config.ADMIN_PASSWORD:
        raise HTTPException(503, "Admin is disabled: set the ADMIN_PASSWORD environment variable")
    if not secrets.compare_digest(x_admin_password, config.ADMIN_PASSWORD):  # constant-time compare
        raise HTTPException(401, "Wrong admin password")


# ---------- pages ----------

# Example: react_page() -> frontend/dist/index.html (React decides chat or dashboard from the URL)
#          react_page() -> HTTP 503 with a hint, if the React app was not built yet
def react_page() -> FileResponse:
    index_file = FRONTEND_DIST / "index.html"
    if not index_file.exists():
        raise HTTPException(503, "Frontend not built. Run: cd frontend && npm install && npm run build")
    return FileResponse(index_file)


# Example: GET / -> the chat page
@app.get("/", include_in_schema=False)
def chat_page() -> FileResponse:
    return react_page()


# Example: GET /admin -> the admin dashboard
@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    return react_page()


# ---------- client API ----------

# Example: GET /health -> {"status": "ok", "mode": "mock"}
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": config.LLM_MODE}


# Example: POST /ask {"question": "What is the refund window?"}
#   -> {"answer": "Within 30 days...", "sources": ["refund_policy.pdf p.1", ...], "model": "amazon.nova-micro-v1:0", ...}
#   -> HTTP 429 once the admin's daily question limit is reached
@app.post("/ask")
def ask(request: AskRequest) -> dict:
    current = settings.get_settings()
    if settings.questions_today() >= current["daily_question_limit"]:
        raise HTTPException(429, "Daily question limit reached. Please try again tomorrow.")

    start = time.perf_counter()
    result = rag.answer_question(request.question, current["active_model"], current["max_tokens"])
    cost = pricing.cost_usd(current["active_model"], result["input_tokens"], result["output_tokens"])
    settings.record_question(cost)
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "model": current["active_model"],
        "mode": config.LLM_MODE,
        "latency_ms": round((time.perf_counter() - start) * 1000),
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "cost_usd": round(cost, 6),
    }


# ---------- admin API ----------

# Example: GET /admin/results -> {"report": {"leaderboard": [...], "recommended": "..."}, "answers": [...], "agreement": {...}}
@app.get("/admin/results", dependencies=[Depends(check_admin)])
def admin_results() -> dict:
    return {
        "report": storage.read_json("eval_report.json", None),
        "answers": storage.read_json("eval_judged.json", []),
        "agreement": storage.read_json("judge_agreement.json", None),
        "candidates": config.CANDIDATE_MODELS,
    }


# Example: POST /admin/eval {"models": ["amazon.nova-micro-v1:0"], "sample_size": 5}
#   -> {"run_id": "2026-11-01T10-00-00", "leaderboard": [...], "recommended": "amazon.nova-micro-v1:0", "mode": "mock"}
@app.post("/admin/eval", dependencies=[Depends(check_admin)])
def admin_eval(request: EvalRequest) -> dict:
    unknown = [model for model in request.models if model not in config.CANDIDATE_MODELS]
    if unknown:
        raise HTTPException(400, f"Not a candidate model: {', '.join(unknown)}")
    return run_eval(request.models, request.sample_size)


# Example: GET /admin/settings -> {"active_model": "amazon.nova-micro-v1:0", "max_tokens": 300, ...}
@app.get("/admin/settings", dependencies=[Depends(check_admin)])
def admin_get_settings() -> dict:
    return settings.get_settings()


# Example: PUT /admin/settings {"active_model": "amazon.nova-lite-v1:0", "allowed_models": [...], "max_tokens": 300,
#   "daily_question_limit": 50} -> the saved settings, or HTTP 400 if active_model is not allowed
@app.put("/admin/settings", dependencies=[Depends(check_admin)])
def admin_save_settings(request: SettingsRequest) -> dict:
    try:
        return settings.save_settings(request.model_dump())
    except ValueError as error:
        raise HTTPException(400, str(error))


# Example: GET /admin/usage -> {"today": {"questions": 3, "cost_usd": 0.0002}, "total_cost_usd": 0.0002, "days": {...}}
@app.get("/admin/usage", dependencies=[Depends(check_admin)])
def admin_usage() -> dict:
    return {"today": settings.usage_today(), **settings.get_usage()}
