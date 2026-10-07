# ADK agents — build from repo root: docker build -f agents/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

COPY agents/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the agents/ package path so "agents.interaction..." imports resolve
COPY agents/ /app/agents/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "agents.interaction.main"]
