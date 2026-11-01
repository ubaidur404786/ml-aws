"""Admin settings (active model + limits) and usage counters."""
from datetime import date

from app import config, storage

DEFAULT_SETTINGS = {
    "active_model": config.ACTIVE_MODEL,
    "allowed_models": config.CANDIDATE_MODELS,
    "max_tokens": 300,
    "daily_question_limit": 100,
}


# Example: get_settings() -> {"active_model": "amazon.nova-micro-v1:0", "max_tokens": 300, ...}
def get_settings() -> dict:
    return {**DEFAULT_SETTINGS, **storage.read_json("settings.json", {})}


# Example: save_settings({"active_model": "amazon.nova-lite-v1:0", "allowed_models": [...], ...})
#   -> same dict, saved; raises ValueError if the active model is not in allowed_models
def save_settings(new_settings: dict) -> dict:
    if new_settings["active_model"] not in new_settings["allowed_models"]:
        raise ValueError("active_model must be one of allowed_models")
    storage.write_json("settings.json", new_settings)
    return new_settings


# Example: get_usage() -> {"days": {"2026-11-01": {"questions": 3, "cost_usd": 0.0002}}, "total_cost_usd": 0.0002}
def get_usage() -> dict:
    return storage.read_json("usage.json", {"days": {}, "total_cost_usd": 0.0})


# Example: usage_today() -> {"questions": 3, "cost_usd": 0.0002}
def usage_today() -> dict:
    return get_usage()["days"].get(date.today().isoformat(), {"questions": 0, "cost_usd": 0.0})


# Example: questions_today() -> 3
def questions_today() -> int:
    return usage_today()["questions"]


# Example: record_question(0.00004) -> adds 1 question and $0.00004 to today's usage
def record_question(cost_usd: float) -> None:
    usage = get_usage()
    today = usage["days"].setdefault(date.today().isoformat(), {"questions": 0, "cost_usd": 0.0})
    today["questions"] += 1
    today["cost_usd"] += cost_usd
    usage["total_cost_usd"] += cost_usd
    storage.write_json("usage.json", usage)
