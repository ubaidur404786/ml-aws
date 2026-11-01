"""Settings read from environment variables (see .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # read .env if it exists (real environment variables win)

# Example: LLM_MODE unset -> "mock"
LLM_MODE = os.getenv("LLM_MODE", "mock")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "amazon.nova-micro-v1:0")
EMBED_MODEL = os.getenv("EMBED_MODEL", "amazon.titan-embed-text-v2:0")
EMBED_DIM = 512  # Titan v2 supports 256, 512 or 1024

# Models the evaluation compares, and the judge model that scores them (must NOT be a candidate).
CANDIDATE_MODELS = os.getenv(
    "CANDIDATE_MODELS", "amazon.nova-micro-v1:0,amazon.nova-lite-v1:0,amazon.nova-pro-v1:0"
).split(",")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "amazon.nova-premier-v1:0")

# Admin dashboard password. Empty means the admin API is switched off.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", PROJECT_DIR / "data" / "docs"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", PROJECT_DIR / "index"))
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", PROJECT_DIR / "storage"))  # settings, usage, eval results
GOLDEN_FILE = PROJECT_DIR / "data" / "golden.jsonl"
