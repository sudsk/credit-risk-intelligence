"""
FastAPI Main Application
SME Credit Intelligence Platform API
"""
import logging
import uvicorn
import httpx
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Services
from services.portfolio_service import get_portfolio_service
from services.risk_engine import get_risk_engine
from services.scenario_job_service import get_scenario_job_service
from services.news_service import get_news_service
from services.task_service import get_task_service
from services.alert_service import get_alert_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise all services at startup."""
    logger.info("Initialising services...")
    # Eagerly instantiate singletons so first-request latency is low
    get_portfolio_service()
    get_risk_engine()
    get_scenario_job_service()
    get_news_service()
    get_task_service()
    get_alert_service()
    logger.info("All services ready")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="SME Credit Intelligence Platform API",
    description="AI-powered credit risk monitoring with alternative data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ScenarioRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class TaskCreateRequest(BaseModel):
    id: str
    title: str
    sme_id: str
    sme_name: str
    priority: str = "medium"
    status: str = "pending"
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Root / Health
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "SME Credit Intelligence Platform API",
        "version": "1.0.0",
        "status": "healthy",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": "port 8080"}


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """Portfolio overview — risk distribution, sector breakdown, totals."""
    try:
        return await get_portfolio_service().get_portfolio_summary()
    except Exception as e:
        logger.error(f"Portfolio summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/smes")
async def get_smes(
    risk_category: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    geography: Optional[str] = Query(None),
    trend: Optional[str] = Query(None),
    min_exposure: Optional[float] = Query(None),
    max_exposure: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("risk_score"),
    sort_order: str = Query("desc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Filtered and sorted SME list."""
    try:
        return await get_portfolio_service().get_sme_list(
            risk_category=risk_category,
            sector=sector,
            geography=geography,
            trend=trend,
            min_exposure=min_exposure,
            max_exposure=max_exposure,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Get SMEs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/smes/{sme_id}")
async def get_sme_detail(sme_id: str):
    """Full SME profile with risk analysis."""
    try:
        return await get_portfolio_service().get_sme_detail(sme_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get SME detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/critical")
async def get_critical_smes(limit: int = Query(20, ge=1, le=100)):
    """SMEs in critical risk category (risk score ≥ 60)."""
    try:
        critical = await get_portfolio_service().get_critical_smes(limit=limit)
        return {"smes": critical, "count": len(critical)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/sectors/{sector}")
async def get_sector_breakdown(sector: str):
    """Breakdown for a specific sector."""
    try:
        return await get_portfolio_service().get_sector_breakdown(sector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/search")
async def search_smes(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50)):
    """Search SMEs by name."""
    try:
        smes = await get_portfolio_service().search_smes(q, limit=limit)
        return {"query": q, "results": smes, "count": len(smes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Change 6 — route 1
@app.get("/api/v1/portfolio/breakdown/{risk_level}")
async def get_portfolio_breakdown(risk_level: str):
    """Sector + geography breakdown for a specific risk level (critical/medium/stable)."""
    if risk_level not in ("critical", "medium", "stable"):
        raise HTTPException(status_code=400, detail="risk_level must be critical, medium, or stable")
    try:
        return await get_portfolio_service().get_breakdown_by_risk(risk_level)
    except Exception as e:
        logger.error(f"Portfolio breakdown error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# SME Risk endpoints (called by agents)
# ---------------------------------------------------------------------------

@app.get("/api/v1/sme/{sme_id}/risk")
async def get_sme_risk(sme_id: str):
    """Computed risk score and top drivers for a specific SME."""
    try:
        return await get_risk_engine().calculate_risk_score(sme_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Risk score error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sme/{sme_id}/peers")
async def get_sme_peers(sme_id: str):
    """Peer comparison — SMEs in same sector and size band."""
    try:
        sme_detail = await get_portfolio_service().get_sme_detail(sme_id)
        sector = sme_detail.get("sector", "")
        peers_result = await get_portfolio_service().get_sme_list(
            sector=sector,
            sort_by="risk_score",
            sort_order="desc",
            limit=10,
        )
        # Exclude the SME itself
        peers = [p for p in peers_result["smes"] if p["id"] != sme_id][:5]
        return {
            "sme_id": sme_id,
            "sector": sector,
            "peers": peers,
            "peer_avg_risk_score": (
                round(sum(p["risk_score"] for p in peers) / len(peers), 1) if peers else 0
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Peer comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Scenarios — async job pattern (Change 7)
# ---------------------------------------------------------------------------

@app.post("/api/v1/scenarios/run")
async def run_scenario(request: ScenarioRequest):
    """
    Start a scenario simulation. Returns job_id immediately.
    Poll GET /api/v1/scenarios/{job_id}/status for results.
    """
    try:
        job_id = get_scenario_job_service().create_job(
            request.scenario_type,
            request.parameters,
        )
        return {
            "job_id": job_id,
            "status": "running",
            "message": f"Scenario '{request.scenario_type}' started. Poll /api/v1/scenarios/{job_id}/status for results.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/scenarios/{job_id}/status")
async def get_scenario_status(job_id: str):
    """Poll scenario job status. When status == 'completed', result is included."""
    job = get_scenario_job_service().get_job_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@app.get("/api/v1/scenarios/templates")
async def get_scenario_templates():
    """Available scenario templates with parameter descriptions."""
    return {
        "templates": [
            {
                "scenario_type": "interest_rate",
                "name": "Interest Rate Shock",
                "description": "Apply bank's interest rate stress vectors to portfolio",
                "parameters": {
                    "rate_increase_bps": {
                        "type": "number",
                        "description": "Rate increase in basis points",
                        "default": 200,
                        "options": [100, 200, 300],
                    }
                },
            },
            {
                "scenario_type": "sector_shock",
                "name": "Sector-Specific Shock",
                "description": "Simulate downturn in a specific sector",
                "parameters": {
                    "sector": {
                        "type": "string",
                        "options": ["Retail/Fashion", "Construction", "Food/Hospitality", "Manufacturing", "Software/Technology"],
                        "example": "Retail/Fashion",
                    },
                    "revenue_impact_pct": {"type": "number", "default": -20},
                },
            },
            {
                "scenario_type": "recession",
                "name": "Economic Recession",
                "description": "Apply bank's recession stress vectors",
                "parameters": {
                    "severity": {
                        "type": "string",
                        "options": ["mild", "moderate", "severe"],
                        "default": "moderate",
                    },
                    "duration_months": {"type": "number", "default": 12},
                },
            },
            {
                "scenario_type": "regulation",
                "name": "Regulatory Change",
                "description": "Simulate impact of new regulation on affected sectors",
                "parameters": {
                    "regulation": {"type": "string", "example": "Hemp Products Ban"},
                    "affected_sectors": {"type": "array", "example": ["Food/Hospitality"]},
                    "revenue_at_risk_pct": {"type": "number", "default": 30},
                },
            },
        ]
    }


# ---------------------------------------------------------------------------
# Scenario: affected SMEs + impact calculation (called by scenario agent)
# ---------------------------------------------------------------------------

@app.post("/api/v1/scenarios/affected-smes")
async def get_affected_smes(request: Dict[str, Any]):
    """
    Return SME IDs affected by a given scenario type and parameters.
    Called by the scenario agent's identify_affected_smes tool.
    """
    scenario_type = request.get("scenario_type", "")
    parameters = request.get("parameters", {})
    try:
        smes_result = await get_portfolio_service().get_sme_list(limit=500)
        all_smes = smes_result["smes"]

        if scenario_type == "sector_shock":
            sector = parameters.get("sector", "")
            affected = [s["id"] for s in all_smes if s["sector"] == sector]
        elif scenario_type == "interest_rate":
            # High-debt sectors most affected
            sensitive_sectors = {"Construction", "Retail/Fashion", "Food/Hospitality", "Logistics"}
            affected = [s["id"] for s in all_smes if s["sector"] in sensitive_sectors]
        elif scenario_type == "regulation":
            sectors = set(parameters.get("affected_sectors", []))
            affected = [s["id"] for s in all_smes if s["sector"] in sectors]
        else:
            # Recession / economic — all SMEs affected
            affected = [s["id"] for s in all_smes]

        return {"sme_ids": affected, "total": len(affected)}
    except Exception as e:
        logger.error(f"Affected SMEs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scenarios/calculate-impact")
async def calculate_scenario_impact(request: Dict[str, Any]):
    """
    Calculate impact for a list of SME IDs under a scenario.
    Called by the scenario agent's calculate_portfolio_impact tool.
    """
    scenario_type = request.get("scenario_type", "")
    parameters = request.get("parameters", {})
    sme_ids = request.get("sme_ids", [])
    try:
        result = await get_scenario_job_service().scenario_service.run_scenario(
            scenario_type, parameters
        )
        # Filter to only the requested SME IDs
        all_impacted = result.get("top_impacted_smes", result.get("impacted_smes", []))
        filtered = [s for s in all_impacted if s.get("id") in set(sme_ids)]
        result["sme_impacts"] = filtered
        return result
    except Exception as e:
        logger.error(f"Impact calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Chat — proxied to agents on port 8080 (Change 4)
# ---------------------------------------------------------------------------

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    Proxy to ADK agents on port 8080.
    Agents expose POST /chat (not /orchestrate — orchestrator removed).
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8080/chat",
                json={"message": request.query, "session_id": request.session_id},
            )
            response.raise_for_status()
            data = response.json()
            return {
                "answer": data["response"],
                "type": "adk_agent",
                "session_id": request.session_id,
            }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to agent service. Ensure ADK agents are running on port 8080.",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=503, detail=f"Agent service error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Chat proxy error: {e}")
        raise HTTPException(status_code=503, detail=f"Agent service unavailable: {str(e)}")


# ---------------------------------------------------------------------------
# Risk (direct calculation endpoints)
# ---------------------------------------------------------------------------

@app.get("/api/v1/risk/calculate/{sme_id}")
async def calculate_risk(sme_id: str):
    try:
        return await get_risk_engine().calculate_risk_score(sme_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/risk/batch")
async def calculate_batch_risk(sme_ids: List[str]):
    try:
        results = await get_risk_engine().batch_calculate_risk_scores(sme_ids)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Change 6 — News routes (routes 2 & 3)
# ---------------------------------------------------------------------------

@app.get("/api/v1/news/intelligence")
async def get_news_intelligence(
    sme_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """News events feed — filterable by SME and severity."""
    try:
        return await get_news_service().get_news_intelligence(
            sme_id=sme_id, severity=severity, limit=limit
        )
    except Exception as e:
        logger.error(f"News intelligence error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/news/predicted-events")
async def get_predicted_events():
    """AI-predicted upcoming risk events for the portfolio."""
    try:
        return await get_news_service().get_predicted_events()
    except Exception as e:
        logger.error(f"Predicted events error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Change 6 — Task routes (routes 4, 5, 6)
# ---------------------------------------------------------------------------

@app.get("/api/v1/tasks")
async def get_tasks(status: Optional[str] = Query(None)):
    """Get all tasks, optionally filtered by status."""
    try:
        return await get_task_service().get_tasks(status=status)
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tasks", status_code=201)
async def create_task(request: TaskCreateRequest):
    """Create a new task."""
    try:
        return await get_task_service().create_task(request.model_dump())
    except Exception as e:
        logger.error(f"Create task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/tasks/{task_id}")
async def update_task(task_id: str, request: TaskUpdateRequest):
    """Update an existing task."""
    try:
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        return await get_task_service().update_task(task_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Change 6 + 8 — Alert routes (route 8)
# ---------------------------------------------------------------------------

@app.post("/api/v1/alerts/simulate")
async def simulate_alert():
    """
    Simulate the TechStart Solutions multi-signal alert.
    Central to the POC demo — fires the 'aha moment'.
    """
    try:
        return await get_alert_service().simulate_alert()
    except Exception as e:
        logger.error(f"Alert simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/alerts")
async def get_active_alerts(limit: int = Query(10, ge=1, le=50)):
    """Active alerts for the portfolio."""
    try:
        return await get_alert_service().get_active_alerts(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")