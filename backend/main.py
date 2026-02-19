"""
FastAPI Main Application
SME Credit Intelligence Platform API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import httpx
import logging

# Import services
from services.portfolio_service import get_portfolio_service
from services.risk_engine import get_risk_engine
from services.scenario_service import get_scenario_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SME Credit Intelligence Platform API",
    description="AI-powered credit risk monitoring with alternative data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
portfolio_service = get_portfolio_service()
risk_engine = get_risk_engine()
scenario_service = get_scenario_service()

# Pydantic models for request/response
class ScenarioRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

# Health check
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "SME Credit Intelligence Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "architecture": "ADK Agent-Powered",
        "endpoints": {
            "portfolio": "/api/v1/portfolio/*",
            "scenarios": "/api/v1/scenarios/*",
            "chat": "/api/v1/chat",
            "risk": "/api/v1/risk/*"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": "required on port 8080"}

# Portfolio endpoints
@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio overview with risk distribution and metrics."""
    try:
        summary = await portfolio_service.get_portfolio_summary()
        return summary
    except Exception as e:
        logger.error(f"Portfolio summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/smes")
async def get_smes(
    risk_category: Optional[str] = Query(None, description="Filter by risk category (critical/medium/stable)"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    geography: Optional[str] = Query(None, description="Filter by geography"),
    trend: Optional[str] = Query(None, description="Filter by trend (up/down/stable)"),
    min_exposure: Optional[float] = Query(None, description="Minimum exposure"),
    max_exposure: Optional[float] = Query(None, description="Maximum exposure"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort_by: str = Query("risk_score", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(100, description="Max results", ge=1, le=500),
    offset: int = Query(0, description="Pagination offset", ge=0)
):
    """Get filtered and sorted list of SMEs."""
    try:
        result = await portfolio_service.get_sme_list(
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
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"Get SMEs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/smes/{sme_id}")
async def get_sme_detail(sme_id: str):
    """Get detailed profile for a specific SME including comprehensive risk analysis."""
    try:
        detail = await portfolio_service.get_sme_detail(sme_id)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get SME detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/critical")
async def get_critical_smes(limit: int = Query(20, ge=1, le=100)):
    """Get SMEs in critical risk category (risk score ≥ 60)."""
    try:
        critical = await portfolio_service.get_critical_smes(limit=limit)
        return {"smes": critical, "count": len(critical)}
    except Exception as e:
        logger.error(f"Get critical SMEs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/sectors/{sector}")
async def get_sector_breakdown(sector: str):
    """Get detailed breakdown for a specific sector."""
    try:
        breakdown = await portfolio_service.get_sector_breakdown(sector)
        return breakdown
    except Exception as e:
        logger.error(f"Get sector breakdown error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/search")
async def search_smes(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50)):
    """Search SMEs by name."""
    try:
        smes = await portfolio_service.search_smes(q, limit=limit)
        return {"query": q, "results": smes, "count": len(smes)}
    except Exception as e:
        logger.error(f"Search SMEs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scenario endpoints
@app.post("/api/v1/scenarios/run")
async def run_scenario(request: ScenarioRequest):
    """
    Run stress test scenario using bank's pre-calculated vectors.
    
    IMPORTANT: This does NOT re-run your full stress test model. 
    Instead, it applies the PD/LGD vectors from your most recent 
    CCAR/ICAAP stress test to the current portfolio composition.
    
    Request Body:
        {
            "scenario_type": "interest_rate" | "sector_shock" | "recession" | "regulation",
            "parameters": {...}
        }
    
    Returns:
        Portfolio impact using your bank's stress vectors.
        ADK agents will generate recommendations from this data.
    """
    try:
        result = await scenario_service.run_scenario(
            request.scenario_type,
            request.parameters
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/scenarios/templates")
async def get_scenario_templates():
    """Get available scenario templates with parameter descriptions."""
    templates = [
        {
            "scenario_type": "interest_rate",
            "name": "Interest Rate Shock",
            "description": "Apply bank's interest rate stress vectors to portfolio",
            "parameters": {
                "rate_increase_bps": {
                    "type": "number",
                    "description": "Interest rate increase in basis points (100, 200, or 300)",
                    "default": 200,
                    "options": [100, 200, 300],
                    "example": 200
                }
            }
        },
        {
            "scenario_type": "sector_shock",
            "name": "Sector-Specific Shock",
            "description": "Simulate downturn in specific sector",
            "parameters": {
                "sector": {
                    "type": "string",
                    "description": "Sector name",
                    "options": ["Retail/Fashion", "Construction", "Food/Hospitality", "Manufacturing", "Software/Technology"],
                    "example": "Retail/Fashion"
                },
                "revenue_impact_pct": {
                    "type": "number",
                    "description": "Revenue impact percentage (negative)",
                    "default": -20,
                    "example": -20
                }
            }
        },
        {
            "scenario_type": "recession",
            "name": "Economic Recession",
            "description": "Apply bank's recession stress vectors",
            "parameters": {
                "severity": {
                    "type": "string",
                    "description": "Recession severity",
                    "options": ["mild", "moderate", "severe"],
                    "default": "moderate"
                },
                "duration_months": {
                    "type": "number",
                    "description": "Duration in months",
                    "default": 12,
                    "example": 12
                }
            }
        },
        {
            "scenario_type": "regulation",
            "name": "Regulatory Change",
            "description": "Simulate impact of new regulation",
            "parameters": {
                "regulation": {
                    "type": "string",
                    "description": "Regulation name",
                    "example": "Hemp Products Ban"
                },
                "affected_sectors": {
                    "type": "array",
                    "description": "List of affected sectors",
                    "example": ["Food/Hospitality", "Retail/Fashion"]
                },
                "revenue_at_risk_pct": {
                    "type": "number",
                    "description": "Percentage of revenue at risk",
                    "default": 30,
                    "example": 40
                }
            }
        }
    ]
    
    return {"templates": templates}

# Chat endpoint - ADK Agents Only
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    Process chat via ADK Orchestrator - NO FALLBACK
    
    Requires ADK agents running on port 8080
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8080/orchestrate",
                json={
                    "message": request.query,
                    "session_id": request.session_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                "answer": data["response"],
                "type": "adk_agent",
                "session_id": request.session_id
            }
    except httpx.HTTPStatusError as e:
        logger.error(f"Agent orchestrator HTTP error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Agent service error: {e.response.status_code}. Ensure agents are running on port 8080."
        )
    except httpx.ConnectError:
        logger.error("Cannot connect to agent orchestrator")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to agent service. Please ensure ADK agents are running on port 8080."
        )
    except Exception as e:
        logger.error(f"Agent orchestrator failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Agent service unavailable: {str(e)}"
        )

# Risk calculation endpoints
@app.get("/api/v1/risk/calculate/{sme_id}")
async def calculate_risk(sme_id: str):
    """Calculate comprehensive risk score for an SME."""
    try:
        risk_analysis = await risk_engine.calculate_risk_score(sme_id)
        return risk_analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Risk calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/risk/batch")
async def calculate_batch_risk(sme_ids: List[str]):
    """Calculate risk scores for multiple SMEs."""
    try:
        results = await risk_engine.batch_calculate_risk_scores(sme_ids)
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Batch risk calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )