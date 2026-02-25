# SME Credit Intelligence Platform

AI-powered credit risk monitoring for SME portfolios. Detects defaults **6–8 weeks earlier** than traditional methods using alternative data signals via Google ADK agents and MCP servers.

---

## Architecture

```
React Frontend (3000)
        │
FastAPI Backend (8000)
        │
ADK Agents Server (8080)
  ├── Chat Agent      — general portfolio queries
  ├── Scenario Agent  — what-if stress analysis
  └── SME Agent       — deep SME analysis
        │
MCP Data Server (8001)
  data_server.py      — unified server, all CSV tools
        │
CSV Data Layer  mcp-servers/data/
```

> **Note:** The six individual MCP servers (companies_house, financial, linkedin, news, payment_data, web_traffic) were consolidated into a single `data_server.py` for the POC. One process, one port, all CSVs loaded at startup.

---

## Project Structure

```
/
├── mcp-servers/
│   ├── data/                          # CSV datasets (smes, alerts, employees…)
│   └── data_sources/
│       └── data_server.py             # Unified MCP server (port 8001)
├── agents/
│   ├── interaction/
│   │   ├── chat_agent.py
│   │   ├── scenario_agent.py
│   │   ├── sme_agent.py
│   │   └── prompts.py
│   ├── shared/
│   │   ├── config.py                  # Env-driven config
│   │   └── mcp_client.py
│   ├── requirements.txt
│   └── main.py                        # FastAPI server (port 8080)
├── backend/
│   ├── data/                          # alerts.csv lives here
│   ├── services/
│   │   ├── portfolio_service.py
│   │   ├── risk_engine.py
│   │   ├── scenario_job_service.py
│   │   └── alert_service.py
│   ├── requirements.txt
│   └── main.py                        # FastAPI server (port 8000)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── home/
    │   │   ├── alerts/
    │   │   ├── scenarios/
    │   │   └── chat/
    │   └── services/
    │       ├── api.ts
    │       └── types.ts
    └── package.json
```

---

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

For the ADK agents you also need a Google Cloud project with Vertex AI or a Gemini API key — see **Environment Setup** below.

---

## Quick Start

Open **four terminals** and run each in order. The MCP data server must be up before the agents start.

### Terminal 1 — MCP Data Server (port 8001)

```bash
cd mcp-servers
pip install -r requirements.txt
python data_sources/data_server.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Terminal 2 — ADK Agents (port 8080)

```bash
cd agents
pip install -r requirements.txt
```

Copy and fill in the environment file:
```bash
cp .env.example .env   # then edit .env — see Environment Setup below
```

Start the server:
```bash
cd ..
python -m agents.interaction.main &
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Terminal 3 — Backend API (port 8000)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000 (reload)
```

### Terminal 4 — Frontend (port 3000)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Environment Setup

The ADK agents need Google Cloud credentials to call Gemini. Create `agents/.env`:

```dotenv
# ── Required ────────────────────────────────────────────────────────────────

# Option A: Vertex AI (recommended for production, uses GCP credentials)
GOOGLE_GENAI_USE_VERTEXAI=true
GCP_PROJECT_ID=your-gcp-project-id
VERTEX_AI_LOCATION=europe-west2

# Option B: Gemini API key (simpler for local dev)
# GOOGLE_GENAI_USE_VERTEXAI=false
# GOOGLE_GENAI_API_KEY=your-gemini-api-key

# ── Optional overrides (defaults shown) ──────────────────────────────────────
GEMINI_MODEL=gemini-2.5-flash
MCP_SERVER_URL=http://localhost:8001
BACKEND_API_URL=http://localhost:8000
```

**Option A — Vertex AI:** Make sure you have application default credentials configured:
```bash
gcloud auth application-default login
gcloud config set project your-gcp-project-id
```

**Option B — Gemini API key:** Get a key from [aistudio.google.com](https://aistudio.google.com/). No GCP project required.

Neither the MCP data server nor the backend need any API keys — they read from CSV only.

---

## UI Tabs

| Tab | What it shows |
|---|---|
| **Home** | Portfolio metrics, SME list, risk breakdown, SME detail panel |
| **Alerts** | Historic + simulated live alerts with signals and recommendations |
| **Scenarios** | Stress test runner with 3-tier recommendations |

The **Simulate Live Feed** button on the Alerts tab fires the TechStart Solutions demo alert — the POC "aha moment".

---

## API Endpoints

**Portfolio**
```
GET  /api/v1/portfolio/summary
GET  /api/v1/portfolio/smes
GET  /api/v1/portfolio/smes/{id}
GET  /api/v1/portfolio/critical
GET  /api/v1/portfolio/breakdown/{risk_level}
GET  /api/v1/portfolio/search?q=
```

**Risk**
```
GET  /api/v1/sme/{id}/risk
GET  /api/v1/sme/{id}/peers
```

**Scenarios**
```
POST /api/v1/scenarios/run
GET  /api/v1/scenarios/{job_id}/status
GET  /api/v1/scenarios/templates
```

**Alerts**
```
POST /api/v1/alerts/simulate
GET  /api/v1/alerts/history
```

**Chat**
```
POST /api/v1/chat
```

Interactive API docs: `http://localhost:8000/docs`

---

## Example Chat Queries

```
"Give me a portfolio summary"
"Which SMEs are critical risk?"
"Analyse TechStart Solutions"
"What if interest rates rise 2%?"
"Show SMEs with executive departures"
"Which companies have payment issues?"
```

Agent routing is automatic — scenario questions go to the Scenario Agent, SME deep-dives to the SME Agent, everything else to the Chat Agent.

---

## Example Scenario Requests

```json
POST /api/v1/scenarios/run

// Interest rate shock
{ "scenario_type": "interest_rate", "parameters": { "rate_increase_bps": 200 } }

// EBA 2025 Adverse scenario
{ "scenario_type": "eba_2025_adverse", "parameters": {} }

// Sector shock
{ "scenario_type": "sector_shock", "parameters": { "sector": "Retail/Fashion", "revenue_impact_pct": -20 } }

// Recession
{ "scenario_type": "recession", "parameters": { "severity": "moderate", "duration_months": 12 } }
```

---

## Risk Model

```
Risk Score = (Financial × 0.40) + (Operational × 0.25) + (Market × 0.20) + (Alt Data × 0.15)
```

| Range | Category | Action |
|---|---|---|
| 0–35 | Stable (Green) | Routine monitoring |
| 35–60 | Medium (Yellow) | Elevated — review required |
| 60–100 | Critical (Red) | Immediate action |

Default probability uses a logistic model with alternative data multipliers:
- C-level departure unreplaced → PD × 1.3
- Web traffic decline >40% → PD × 1.4
- Critical news event → PD × 1.5
- Late payments >10 → PD × 1.25

Signal impact weights on risk score:

| Signal | Score impact |
|---|---|
| CEO / CFO / CTO departure | +12 pts |
| C-level departure (other) | +10 pts |
| Web traffic decline >40% | +8 pts |
| Payment delays detected | +5 pts |
| Adverse news event | +3 pts |

---

## Demo: TechStart Solutions

The POC demo centres on SME `#0142 TechStart Solutions` — risk score escalated from **45 → 68** driven by three simultaneous signals:

| Signal | Detail | Risk Contribution |
|---|---|---|
| CTO departure (unreplaced) | Co-founder, 4yr tenure | +12 pts |
| Web traffic −42% QoQ | Bounce rate 38% → 58% | +8 pts |
| Payment delays increasing | Avg days late: 3 → 12 | +5 pts |

**Rating gap:** Live indicative grade **B** vs bank's quarterly rating **BB+** (2-notch lag). PD moved from **3.0% → 5.4%** due to these signals. Traditional banking detects this at next quarterly review. The platform flags it in real time.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Recharts, EPAM Loveship Dark |
| Backend | FastAPI, Python 3.11, Pydantic |
| Agents | Google ADK 1.25.0, Gemini 2.5 Flash |
| MCP | FastMCP, Streamable HTTP |
| Data | Pandas, CSV (100 SMEs) |

---

## Troubleshooting

**MCP data server not starting**
```bash
cd mcp-servers
pip install fastmcp pandas
ls data/   # verify CSV files exist (smes.csv, employees.csv, etc.)
python data_sources/data_server.py
```

**Agents not responding / MCP connection error**
```bash
# Verify the MCP server is up first
curl http://localhost:8001/mcp

# Check agents/.env is populated
cat agents/.env

# If using Vertex AI, verify GCP credentials
gcloud auth application-default print-access-token
```

**Frontend not loading data**
```bash
# Test backend is healthy
curl http://localhost:8000/api/v1/portfolio/summary

# Check CORS — frontend must be on port 3000
# Check browser console for errors
```

**Chat returning errors**
```bash
# Test agents server directly
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "portfolio summary", "session_id": "test"}'
```

**Port conflicts**
```bash
lsof -ti:8001 | xargs kill -9   # MCP data server
lsof -ti:8080 | xargs kill -9   # agents
lsof -ti:8000 | xargs kill -9   # backend
lsof -ti:3000 | xargs kill -9   # frontend
```

---

## Cloud Run Deployment

```bash
# MCP Data Server
gcloud run deploy mcp-data-server \
  --source=./mcp-servers \
  --region=europe-west2 \
  --set-env-vars="PORT=8001"

# Agents
gcloud run deploy agents \
  --source=./agents \
  --region=europe-west2 \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=true,GCP_PROJECT_ID=your-project-id,VERTEX_AI_LOCATION=europe-west2"

# Backend
gcloud run deploy backend-api \
  --source=./backend \
  --region=europe-west2

# Frontend
vercel deploy
```

After deploying, update `agents/.env` (or Cloud Run env vars) with the live URLs:
```
MCP_SERVER_URL=https://mcp-data-server-xxx.run.app
BACKEND_API_URL=https://backend-api-xxx.run.app
```