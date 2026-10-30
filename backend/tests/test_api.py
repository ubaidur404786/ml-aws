"""API tests. Run from the backend folder:  pytest"""
from fastapi.testclient import TestClient

from app.main import app

EXAMPLE_CUSTOMER = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 2,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 95.5,
    "TotalCharges": 190.0,
}


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_loaded": True}


def test_predict_valid_customer():
    with TestClient(app) as client:
        response = client.post("/api/predict", json=EXAMPLE_CUSTOMER)
        assert response.status_code == 200
        body = response.json()
        assert 0 <= body["churn_probability"] <= 1
        # A new month-to-month fiber customer is a classic high-risk profile
        assert body["churn"] is True


def test_predict_invalid_customer():
    bad_customer = {**EXAMPLE_CUSTOMER, "Contract": "Weekly", "tenure": -5}
    with TestClient(app) as client:
        response = client.post("/api/predict", json=bad_customer)
        assert response.status_code == 422
