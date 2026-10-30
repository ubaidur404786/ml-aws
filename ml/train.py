"""Train a customer churn model and save it for the FastAPI backend.

Steps: load data -> clean -> split -> build pipeline -> train 2 models
-> evaluate -> pick the best -> save pipeline + metrics.

Run:  python train.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ML_DIR = Path(__file__).parent
DATA_FILE = ML_DIR / "data" / "Telco-Customer-Churn.csv"
REPORT_FILE = ML_DIR / "reports" / "metrics.json"
# The backend loads the model from here (it is copied into the Docker image)
MODEL_FILE = ML_DIR.parent / "backend" / "model" / "churn_pipeline.joblib"

RANDOM_STATE = 42

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
CATEGORICAL_FEATURES = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_and_clean_data() -> pd.DataFrame:
    """Read the CSV and fix the known data issues."""
    if not DATA_FILE.exists():
        raise SystemExit("Dataset not found. Run: python download_data.py")

    df = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns")

    # customerID is only an identifier, not useful for prediction
    df = df.drop(columns=["customerID"])

    # TotalCharges is text and has blank values for new customers (tenure = 0).
    # Convert to numbers; blanks become NaN and are imputed in the pipeline.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    print(f"Missing TotalCharges values: {df['TotalCharges'].isna().sum()}")

    # Target: Yes -> 1 (churn), No -> 0
    df["Churn"] = (df["Churn"] == "Yes").astype(int)
    print(f"Churn rate: {df['Churn'].mean():.1%}")
    return df


def build_preprocessor() -> ColumnTransformer:
    """Preprocessing that is saved together with the model,
    so the backend applies exactly the same steps at prediction time."""
    numeric_steps = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_steps = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_steps, NUMERIC_FEATURES),
        ("categorical", categorical_steps, CATEGORICAL_FEATURES),
    ])


def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Compute the standard classification metrics on the test set."""
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": round(accuracy_score(y_test, predictions), 4),
        "precision": round(precision_score(y_test, predictions), 4),
        "recall": round(recall_score(y_test, predictions), 4),
        "f1": round(f1_score(y_test, predictions), 4),
        "roc_auc": round(roc_auc_score(y_test, probabilities), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }


def main() -> None:
    df = load_and_clean_data()
    X = df[FEATURES]
    y = df["Churn"]

    # 80/20 split; stratify keeps the same churn rate in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    # class_weight="balanced" helps with the imbalanced target (~26% churn)
    candidates = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_leaf=5,
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }

    results = {}
    trained = {}
    for name, classifier in candidates.items():
        pipeline = Pipeline([
            ("preprocess", build_preprocessor()),
            ("model", classifier),
        ])
        cv_auc = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="roc_auc")
        pipeline.fit(X_train, y_train)
        metrics = evaluate(pipeline, X_test, y_test)
        metrics["cv_roc_auc_mean"] = round(cv_auc.mean(), 4)
        results[name] = metrics
        trained[name] = pipeline
        print(f"\n{name}")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

    # Prefer the simpler model (Logistic Regression) unless Random Forest
    # is clearly better (more than 0.01 ROC-AUC)
    lr_auc = results["LogisticRegression"]["roc_auc"]
    rf_auc = results["RandomForest"]["roc_auc"]
    best_name = "RandomForest" if rf_auc - lr_auc > 0.01 else "LogisticRegression"
    print(f"\nSelected model: {best_name}")

    # Save the full pipeline (preprocessing + model) with some metadata
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": trained[best_name],
            "model_name": best_name,
            "features": FEATURES,
            "threshold": 0.5,
            "sklearn_version": sklearn.__version__,
            "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "metrics": results[best_name],
        },
        MODEL_FILE,
    )
    print(f"Model saved to {MODEL_FILE}")

    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps({"selected_model": best_name, "models": results}, indent=2)
    )
    print(f"Metrics saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
