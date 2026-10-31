"""Settings read from environment variables (see .env.example)."""
import os
from pathlib import Path

# Example: LLM_MODE unset -> "mock"
LLM_MODE = os.getenv("LLM_MODE", "mock")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "amazon.nova-micro-v1:0")
EMBED_MODEL = os.getenv("EMBED_MODEL", "amazon.titan-embed-text-v2:0")
EMBED_DIM = 512  # Titan v2 supports 256, 512 or 1024

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", PROJECT_DIR / "data" / "docs"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", PROJECT_DIR / "index"))
