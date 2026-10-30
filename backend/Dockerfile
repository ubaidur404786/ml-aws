# Backend image: FastAPI + the trained model
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (this layer is cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the trained model
COPY app/ ./app/
COPY model/ ./model/

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Docker marks the container unhealthy if /api/health stops responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
