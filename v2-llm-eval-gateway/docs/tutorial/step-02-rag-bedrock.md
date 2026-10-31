# Step 2: RAG with Bedrock + golden set

**Goal:** real retrieval (PDFs → chunks → Titan embeddings → FAISS → top-k → Nova answer + sources) and a 10-row golden dataset.

## What was created

| File | Purpose |
|---|---|
| `scripts/make_sample_pdfs.py` | Creates 3 small sample PDFs about a made-up shop in `data/docs/` |
| `app/documents.py` | Reads PDF pages and splits them into chunks |
| `app/embeddings.py` | Text → vector (Titan v2, or a free fake in mock mode) |
| `app/ingest.py` | Builds the FAISS index in `index/` |
| `app/rag.py` | Searches the index, builds the "answer only from context" prompt, asks the model |
| `app/llm.py` | Calls Bedrock with the Converse API (or a fake answer in mock mode) |
| `data/golden.jsonl` | 10 hand-written questions: 5 easy, 3 multi, 2 unanswerable |
| `scripts/draft_golden.py` | Drafts golden questions from your own PDFs (review every row by hand) |
| `scripts/ask_golden.py` | Asks every golden question once and prints the answers |

## Part A: mock mode (free) ✅

1. Install the new packages:
```bash
pip install -r requirements.txt
```

2. Create the sample PDFs:
```bash
python scripts/make_sample_pdfs.py
```

3. Build the index:
```bash
python -m app.ingest
```
Output ([log](logs/step-02-ingest-mock.txt)):
```
Indexed 6 chunks from ./data\docs (mock embeddings) -> ./index
```

4. Ask the golden questions:
```bash
python scripts/ask_golden.py
```
Output, first rows ([log](logs/step-02-ask-golden-mock.txt)):
```
#1 [easy] How many days do I have to ask for a refund?
   answer:   [MOCK] Based on the context: Exceptions and processing Digital items ...
   sources:  refund_policy.pdf p.2, refund_policy.pdf p.1, shipping_guide.pdf p.2  (expected: refund_policy.pdf p.1)
```
The mock answers are not meant to be correct. They only prove the pipeline runs end to end.

5. Run the tests:
```bash
pytest -q
```
Output: `6 passed`.

## Part B: real Bedrock (us-east-1) 🟡

1. Log in to AWS. The first time, it asks for a region; press Enter for `us-east-1`:
```bash
aws login
```

2. Check that you are logged in:
```bash
aws sts get-caller-identity
```

3. Check that the models are available:
```bash
aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?contains(modelId,'nova-micro') || contains(modelId,'titan-embed-text-v2')].modelId" --output text
```
Result: `amazon.nova-micro-v1:0` and `amazon.titan-embed-text-v2:0` are listed as ON_DEMAND (pay per call).

4. Check the prices (live AWS Price List, checked 2026-10-31, per 1K tokens): Nova Lite $0.00006 in / $0.00024 out, Nova Pro $0.0008 in / $0.0032 out, Nova Micro $0.00014 out. Expected cost of this step: **under $0.001**.

5. Ingest and ask with real models (PowerShell):
```powershell
$env:LLM_MODE="bedrock"
python -m app.ingest
python scripts/ask_golden.py
```

### Problems and fixes

| Error | Cause | Fix |
|---|---|---|
| `NoCredentialsError: Unable to locate credentials` | `aws login` is new; boto3 1.35 cannot read its credentials | Upgrade to `boto3==1.43.123` |
| `MissingDependencyException: ... pip install "botocore[crt]"` | The `aws login` credential provider needs the CRT add-on | Use `boto3[crt]==1.43.123` in `requirements.txt` |
| `AccessDeniedException: Your account is currently being verified` | A brand-new AWS account cannot call Bedrock until AWS verifies it (usually < 2 hours) | Wait, then re-run step 5. Nothing was charged. |

### Real output

_Will be added here once account verification finishes._
