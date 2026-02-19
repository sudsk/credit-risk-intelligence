# 🐳 Docker Deployment Guide

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- GCP credentials (for Orchestrator)

---

## 📦 File Structure

```
project-root/
├── docker-compose.yml                      # Main orchestration file
├── mcp-servers/
│   ├── Dockerfile.companies-house          # Companies House server
│   ├── Dockerfile.financial                # Financial server
│   ├── Dockerfile.linkedin                 # LinkedIn server
│   ├── Dockerfile.news                     # News server
│   ├── Dockerfile.payment                  # Payment server
│   ├── Dockerfile.web-traffic              # Web traffic server
│   ├── requirements.txt
│   ├── data/                               # CSV files
│   └── data_sources/                       # Server Python files
├── agents/
│   ├── Dockerfile.orchestrator             # ADK Orchestrator
│   ├── requirements.txt
│   └── ...
├── backend/
│   ├── Dockerfile                          # Backend API
│   ├── requirements.txt
│   └── ...
└── frontend/
    ├── Dockerfile                          # Frontend
    ├── package.json
    └── ...
```

---

## 🚀 Quick Start

### 1. Environment Setup

Create `.env` file in project root:

```bash
# GCP Configuration (for Orchestrator)
GCP_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1

# Optional: Override default ports
# COMPANIES_HOUSE_PORT=8001
# FINANCIAL_PORT=8002
# LINKEDIN_PORT=8003
# NEWS_PORT=8004
# PAYMENT_PORT=8005
# WEB_TRAFFIC_PORT=8006
# ORCHESTRATOR_PORT=8080
# BACKEND_PORT=8000
# FRONTEND_PORT=3000
```

### 2. Build All Services

```bash
docker-compose build
```

**Build time:** ~5-10 minutes (first time)

### 3. Start All Services

```bash
docker-compose up
```

Or in detached mode:
```bash
docker-compose up -d
```

### 4. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Should show 11 services:
# - 6 MCP servers (ports 8001-8006)
# - 1 Orchestrator (port 8080)
# - 1 Backend (port 8000)
# - 1 Frontend (port 3000)
```

### 5. Health Checks

```bash
# MCP Servers
curl http://localhost:8001/  # Companies House
curl http://localhost:8002/  # Financial
curl http://localhost:8003/  # LinkedIn
curl http://localhost:8004/  # News
curl http://localhost:8005/  # Payment
curl http://localhost:8006/  # Web Traffic

# Orchestrator
curl http://localhost:8080/health

# Backend
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

---

## 🔧 Service Dependencies

The startup order is managed automatically via health checks:

```
1. MCP Servers (8001-8006)     → Start first, must be healthy
   ↓
2. Orchestrator (8080)          → Waits for all MCP servers
   ↓
3. Backend (8000)               → Waits for Orchestrator
   ↓
4. Frontend (3000)              → Waits for Backend
```

**Total startup time:** ~2-3 minutes

---

## 📊 Resource Usage

| Service | CPU | Memory | Notes |
|---------|-----|--------|-------|
| Each MCP Server | 0.1 core | ~50MB | 6 servers = 300MB |
| Orchestrator | 0.5 core | ~200MB | Gemini API calls |
| Backend | 0.2 core | ~100MB | FastAPI |
| Frontend | 0.1 core | ~50MB | Vite dev server |
| **Total** | **1.5 cores** | **~700MB** | Comfortable on 4GB RAM |

---

## 🛠️ Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f companies-house-server
docker-compose logs -f orchestrator
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart orchestrator
docker-compose restart backend
```

### Stop Services

```bash
# Stop all (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Rebuild Specific Service

```bash
# Rebuild after code changes
docker-compose build companies-house-server
docker-compose up -d companies-house-server

# Force rebuild (no cache)
docker-compose build --no-cache orchestrator
```

---

## 🐛 Troubleshooting

### MCP Server Not Starting

**Symptom:** Container exits immediately

**Check:**
```bash
docker-compose logs companies-house-server

# Common issues:
# 1. Missing pandas
# 2. CSV files not found
# 3. Port already in use
```

**Solution:**
```bash
# Verify requirements.txt has pandas
cat mcp-servers/requirements.txt | grep pandas

# Verify CSV files exist
ls -la mcp-servers/data/

# Check port conflicts
lsof -ti:8001
```

### Orchestrator Connection Errors

**Symptom:** "Connection refused" to MCP servers

**Check:**
```bash
# Verify MCP servers are healthy
docker-compose ps

# Check logs
docker-compose logs orchestrator | grep "MCP"
```

**Solution:**
```bash
# Restart in correct order
docker-compose restart companies-house-server financial-server
docker-compose restart orchestrator
```

### Frontend Not Loading Data

**Symptom:** White screen or API errors

**Check:**
```bash
# Backend health
curl http://localhost:8000/health

# Browser console
# Check for CORS errors or 404s
```

**Solution:**
```bash
# Verify environment variables
docker-compose exec frontend env | grep VITE_API_URL

# Should be: VITE_API_URL=http://localhost:8000
```

### Permission Errors (GCP)

**Symptom:** Orchestrator fails with "Permission denied"

**Check:**
```bash
docker-compose logs orchestrator | grep -i "permission\|auth"
```

**Solution:**
```bash
# Ensure GCP credentials are mounted
ls -la ~/.config/gcloud/

# Rebuild with correct volume mount
docker-compose down
docker-compose up -d
```

---

## 🧪 Testing the Deployment

### 1. Test MCP Servers

```bash
# Test each server's root endpoint
for port in {8001..8006}; do
  echo "Testing port $port..."
  curl -f http://localhost:$port/ && echo "✅ OK" || echo "❌ FAIL"
done
```

### 2. Test Backend API

```bash
# Portfolio summary
curl http://localhost:8000/api/v1/portfolio/summary

# Critical SMEs
curl http://localhost:8000/api/v1/portfolio/critical
```

### 3. Test Orchestrator

```bash
# Health check
curl http://localhost:8080/health

# Query test
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me critical SMEs"}'
```

### 4. Test Frontend

```bash
# Open in browser
open http://localhost:3000

# Or use curl to check it loads
curl -I http://localhost:3000
```

---

## 🔄 Development Workflow

### Hot Reload Enabled

All services support hot reload:

- **Frontend:** Vite watches for file changes
- **Backend:** Uvicorn `--reload` flag
- **Orchestrator:** Python auto-reload
- **MCP Servers:** Manual restart required

### Making Code Changes

```bash
# 1. Edit code in your local directory
vim backend/services/risk_engine.py

# 2. Changes auto-reload (Backend/Frontend/Orchestrator)
# Watch logs:
docker-compose logs -f backend

# 3. MCP servers need manual restart
docker-compose restart companies-house-server
```

### Adding New Dependencies

**Python (Backend/Orchestrator/MCP):**
```bash
# 1. Update requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# 2. Rebuild container
docker-compose build backend

# 3. Restart
docker-compose up -d backend
```

**Node (Frontend):**
```bash
# 1. Update package.json
# 2. Rebuild
docker-compose build frontend
docker-compose up -d frontend
```

---

## 🌐 Network Configuration

All services communicate via Docker's internal network (`foresight-network`):

**Internal URLs (inside Docker):**
- `http://companies-house-server:8001`
- `http://financial-server:8002`
- `http://linkedin-server:8003`
- `http://news-server:8004`
- `http://payment-server:8005`
- `http://web-traffic-server:8006`
- `http://orchestrator:8080`
- `http://backend:8000`
- `http://frontend:3000`

**External URLs (from host):**
- `http://localhost:8001-8006` (MCP servers)
- `http://localhost:8080` (Orchestrator)
- `http://localhost:8000` (Backend)
- `http://localhost:3000` (Frontend)

---

## 📈 Monitoring

### Container Stats

```bash
# Real-time resource usage
docker stats

# Specific services
docker stats companies-house-server orchestrator backend
```

### Health Check Status

```bash
# All services health
docker-compose ps

# Format: SERVICE | STATUS | PORTS
# Look for "(healthy)" in STATUS column
```

---

## 🚀 Production Deployment

For production, use separate Dockerfiles without dev dependencies:

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  # Same structure but:
  # - Remove volume mounts
  # - Use production commands
  # - Add resource limits
  # - Configure restart policies
  
  companies-house-server:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    # ... rest of config
```

### Cloud Run Deployment (Recommended)

Instead of Docker Compose in production, deploy to Cloud Run:

```bash
# Deploy each service separately
gcloud run deploy companies-house-server \
  --source=./mcp-servers \
  --dockerfile=Dockerfile.companies-house \
  --region=europe-west2 \
  --allow-unauthenticated

# Repeat for all 6 MCP servers + Orchestrator + Backend
```

---

## 📚 Additional Resources

- Docker Compose Docs: https://docs.docker.com/compose/
- Dockerfile Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Cloud Run Docs: https://cloud.google.com/run/docs

---

## ✅ Deployment Checklist

- [ ] `.env` file created with GCP credentials
- [ ] All Dockerfiles placed in correct directories
- [ ] `docker-compose.yml` in project root
- [ ] CSV data files in `mcp-servers/data/`
- [ ] GCP credentials mounted (`~/.config/gcloud`)
- [ ] Ports 8000-8006, 8080, 3000 available
- [ ] Docker daemon running
- [ ] 4GB+ RAM available
- [ ] Built all images: `docker-compose build`
- [ ] Started services: `docker-compose up -d`
- [ ] Verified health: `docker-compose ps`
- [ ] Tested frontend: http://localhost:3000

**🎉 Once all checked, your deployment is complete!**