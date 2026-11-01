"""Small JSON files for settings, usage and eval results.

Stored in the local storage/ folder for now. Step 5 moves the same files to S3.
"""
import json

from app import config


# Example: read_json("settings.json", {}) -> {"active_model": "amazon.nova-micro-v1:0", ...}
#          read_json("missing.json", {}) -> {}
def read_json(name: str, default):
    path = config.STORAGE_DIR / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


# Example: write_json("settings.json", {"max_tokens": 300}) -> writes storage/settings.json
def write_json(name: str, data) -> None:
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    (config.STORAGE_DIR / name).write_text(json.dumps(data, indent=2), encoding="utf-8")
