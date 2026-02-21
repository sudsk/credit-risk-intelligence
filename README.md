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
MCP Servers (8001–8004)
  Companies House · Financial · LinkedIn · News
        │
CSV Data Layer  /mcp-servers/data/
```

---

## Quick Start

**Prerequisites:** Python 3.11+, Node.js 18+

```bash
# Install dependencies
cd mcp-servers && pip install -r requirements.txt
cd ../agents   && pip install -r requirements.txt
cd ../backend  && pip install -r requirements.txt
cd ../frontend && npm install
```

**Run (4 terminals):**

```bash
# Terminal 1 — MCP Servers (ports 8001–8004)
cd mcp-servers && python main.py

# Terminal 2 — ADK Agents (port 8080)
cd agents && python main.py

# Terminal 3 — Backend API (port 8000)
cd backend && python main.py

# Terminal 4 — Frontend (port 3000)
cd frontend && npm run dev
```

Open `http://localhost:3000`

---

## Project Structure

```
/
├── mcp-servers/
│   ├── data/                          # 7 CSV datasets
│   └── data_sources/
│       ├── companies_house_server.py  (8001)
│       ├── financial_server.py        (8002)
│       ├── linkedin_server.py         (8003)
│       └── news_server.py             (8004)
├── agents/
│   ├── interaction/
│   │   ├── chat_agent.py
│   │   ├── scenario_agent.py
│   │   ├── sme_agent.py
│   │   └── prompts.py
│   ├── shared/
│   │   ├── config.py
│   │   └── mcp_client.py
│   └── main.py                        # FastAPI server (8080)
├── backend/
│   ├── services/
│   │   ├── portfolio_service.py
│   │   ├── risk_engine.py
│   │   ├── scenario_job_service.py
│   │   └── alert_service.py
│   └── main.py                        # FastAPI server (8000)
└── frontend/
    └── src/
        ├── components/
        │   ├── home/
        │   ├── alerts/                # AlertsTab
        │   ├── scenarios/
        │   └── chat/
        └── services/
            ├── api.ts
            └── types.ts
```

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

---

## Demo: TechStart Solutions

The POC demo centres on SME `#4567 TechStart Solutions` — risk score escalated from **45 → 68** driven by three simultaneous signals:

| Signal | Detail | Risk Contribution |
|---|---|---|
| CTO departure (unreplaced) | Co-founder, 4yr tenure | +12 pts |
| Web traffic −42% QoQ | Bounce rate 38% → 58% | +7 pts |
| Payment delays increasing | Avg days late: 3 → 12 | +4 pts |

Traditional banking detects this at next quarterly review. The platform flags it in real time.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Recharts, EPAM Loveship Dark |
| Backend | FastAPI, Python 3.11, Pydantic |
| Agents | Google ADK 1.25.0, Gemini 2.0 Flash |
| MCP | FastMCP, Streamable HTTP |
| Data | Pandas, CSV (100 SMEs, 2020–2024) |

---

## Troubleshooting

**MCP servers not starting**
```bash
pip install pandas==2.2.0
ls mcp-servers/data/   # verify CSV files exist
```

**Agents not responding**
```bash
curl http://localhost:8001/   # verify MCP servers are up first
cat agents/shared/config.py   # check MCP server URLs
```

**Frontend not loading data**
```bash
curl http://localhost:8000/api/v1/portfolio/summary
# Check browser console for CORS errors
```

**Port conflicts**
```bash
lsof -ti:8000 | xargs kill -9   # backend
lsof -ti:8080 | xargs kill -9   # agents
lsof -ti:3000 | xargs kill -9   # frontend
```

---

## Cloud Run Deployment

```bash
# MCP Servers (one per server)
gcloud run deploy companies-house-server \
  --source=./mcp-servers/data_sources/companies_house_server.py \
  --region=europe-west2

# Agents
gcloud run deploy agents \
  --source=./agents \
  --region=europe-west2

# Backend
gcloud run deploy backend-api \
  --source=./backend \
  --region=europe-west2

# Frontend
vercel deploy
```