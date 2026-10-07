# Backend API — build from repo root: docker build -f backend/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/
# Shared SME CSVs used by the risk engine and scenario service
COPY mcp-servers/data/ /app/mcp-data/

ENV DATA_DIR=/app/mcp-data
ENV PYTHONUNBUFFERED=1

# Cloud Run sets $PORT (default 8080)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
