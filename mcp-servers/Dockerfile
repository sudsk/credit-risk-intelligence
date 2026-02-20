# Unified Data MCP Server 
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ /app/data/
COPY data_sources/data_server.py /app/

ENV PYTHONPATH=/app
ENV PORT=8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/ || exit 1

CMD ["python", "data_server.py"]