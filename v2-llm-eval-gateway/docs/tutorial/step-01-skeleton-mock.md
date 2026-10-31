# Step 1: Folder skeleton + mock API

**Goal:** a tiny FastAPI app with `GET /health` and `POST /ask` that runs locally for free (`LLM_MODE=mock`, no AWS).

## What was created

| File | Purpose |
|---|---|
| `app/config.py` | Reads settings from environment variables |
| `app/rag.py` | Finds matching text and builds the prompt |
| `app/llm.py` | Calls the model (fake answer in mock mode) |
| `app/main.py` | FastAPI routes `/health` and `/ask` |
| `tests/test_api.py` | pytest tests |
| `requirements.txt`, `.env.example`, `.gitignore` | Setup files |
| `README.md` | Project overview with diagrams |

## Commands

1. Create a virtual environment:
```powershell
cd v2-llm-eval-gateway
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install packages:
```bash
pip install -r requirements.txt
```

3. Run the tests:
```bash
pytest -q
```

4. Start the API:
```bash
uvicorn app.main:app --reload
```

5. In a second terminal, call it:
```bash
curl http://localhost:8000/health
```
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"How long does shipping take?\"}"
```

## Output

```
{"status":"ok","mode":"mock"}
{"answer":"[MOCK] Based on the context: Standard shipping takes 3 to 5 business days.",
 "sources":["shipping.pdf p.1","policy.pdf p.2"],"model":"amazon.nova-micro-v1:0","mode":"mock",
 "latency_ms":0,"input_tokens":48,"output_tokens":13}
```
pytest: `3 passed`.

## Problems and fixes

- **A test failed at first.** "What is the refund window?" shares no word with "Refunds are accepted within 30 days" ("refund" is not "refunds"), so the simple word matcher picked the wrong text.
  **Fix:** the test asks "When are refunds accepted?" instead. Lesson: word matching is weak, which is why Step 2 uses embeddings.

## Commit

`Add v2 LLM Eval & Gateway skeleton with mock-mode API and README`
