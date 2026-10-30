"""Load the saved pipeline and make predictions."""
import os
from pathlib import Path

import joblib
import pandas as pd

from app.schemas import CustomerData

DEFAULT_MODEL_PATH = Path(__file__).parent.parent / "model" / "churn_pipeline.joblib"


class ChurnModel:
    def __init__(self) -> None:
        self.bundle: dict | None = None

    def load(self) -> None:
        model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}. Run ml/train.py first.")
        # The bundle holds the full pipeline (preprocessing + model) and metadata
        self.bundle = joblib.load(model_path)

    @property
    def is_loaded(self) -> bool:
        return self.bundle is not None

    def predict(self, customer: CustomerData) -> dict:
        # One-row DataFrame with the same columns used during training.
        # The pipeline applies the same preprocessing as in training.
        row = pd.DataFrame([customer.model_dump()])[self.bundle["features"]]
        probability = float(self.bundle["pipeline"].predict_proba(row)[0, 1])
        will_churn = probability >= self.bundle["threshold"]
        return {
            "churn": will_churn,
            "churn_probability": round(probability, 4),
            "label": "Likely to churn" if will_churn else "Likely to stay",
        }

    def info(self) -> dict:
        return {
            "model_name": self.bundle["model_name"],
            "trained_at": self.bundle["trained_at"],
            "metrics": self.bundle["metrics"],
        }


churn_model = ChurnModel()
