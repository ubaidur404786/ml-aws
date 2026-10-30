"""FastAPI app: health check, model info, and churn prediction."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.model import churn_model
from app.schemas import CustomerData, PredictionResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("churn-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model once when the server starts (not on every request)
    churn_model.load()
    logger.info("Model loaded: %s", churn_model.bundle["model_name"])
    yield


app = FastAPI(title="Customer Churn Prediction API", version="1.0.0", lifespan=lifespan)

# CORS is only needed when the React dev server runs on a different port.
# In Docker, nginx serves the frontend and the API from the same origin.
cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": churn_model.is_loaded}


@app.get("/api/model-info")
def model_info() -> dict:
    return churn_model.info()


@app.post("/api/predict", response_model=PredictionResponse)
def predict(customer: CustomerData) -> dict:
    # Invalid input never reaches this point: FastAPI returns 422 automatically
    try:
        return churn_model.predict(customer)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed. Please try again.")
