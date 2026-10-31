"""Settings read from environment variables (see .env.example)."""
import os

# Example: LLM_MODE unset -> "mock"
LLM_MODE = os.getenv("LLM_MODE", "mock")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "amazon.nova-micro-v1:0")
