# Unified MCP data server — build from repo root: docker build -f mcp-servers/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

COPY mcp-servers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep data/ and data_sources/ side by side — data_server.py reads ../data
COPY mcp-servers/data/ /app/data/
COPY mcp-servers/data_sources/ /app/data_sources/

ENV PYTHONUNBUFFERED=1

CMD ["python", "data_sources/data_server.py"]
