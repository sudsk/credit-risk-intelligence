"""
FastAPI Main Application
SME Credit Intelligence Platform API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn, httpx

# Import services
from services.portfolio_service import get_portfolio_service
from services.risk_engine import get_risk_engine
from services.scenario_service import get_scenario_service
from services.chat_service import get_chat_service

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
chat_service = get_chat_service()

# Pydantic models for request/response
class ScenarioRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]

class ChatRequest(BaseModel):
    query: str
    use_claude_api: bool = False

# Health check
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "SME Credit Intelligence Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "portfolio": "/api/v1/portfolio/*",
            "scenarios": "/api/v1/scenarios/*",
            "chat": "/api/v1/chat"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Portfolio endpoints
@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """
    Get portfolio overview with risk distribution and metrics.
    
    Returns:
        Portfolio summary with exposure, risk distribution, sector breakdown
    """
    try:
        summary = await portfolio_service.get_portfolio_summary()
        return summary
    except Exception as e:
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
    """
    Get filtered and sorted list of SMEs.
    
    Query Parameters:
        - risk_category: Filter by risk level
        - sector: Filter by industry sector
        - geography: Filter by location
        - trend: Filter by growth trend
        - min_exposure/max_exposure: Filter by exposure range
        - search: Search by company name
        - sort_by: Field to sort by
        - sort_order: asc or desc
        - limit: Max results per page
        - offset: Pagination offset
    
    Returns:
        List of SMEs with metadata
    """
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/smes/{sme_id}")
async def get_sme_detail(sme_id: str):
    """
    Get detailed profile for a specific SME including comprehensive risk analysis.
    
    Path Parameters:
        - sme_id: SME identifier
    
    Returns:
        Complete SME profile with risk breakdown
    """
    try:
        detail = await portfolio_service.get_sme_detail(sme_id)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/critical")
async def get_critical_smes(limit: int = Query(20, ge=1, le=100)):
    """
    Get SMEs in critical risk category (risk score ≥ 60).
    
    Query Parameters:
        - limit: Max results
    
    Returns:
        List of critical SMEs sorted by risk score
    """
    try:
        critical = await portfolio_service.get_critical_smes(limit=limit)
        return {"smes": critical, "count": len(critical)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/sectors/{sector}")
async def get_sector_breakdown(sector: str):
    """
    Get detailed breakdown for a specific sector.
    
    Path Parameters:
        - sector: Sector name
    
    Returns:
        Sector statistics and risk distribution
    """
    try:
        breakdown = await portfolio_service.get_sector_breakdown(sector)
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/search")
async def search_smes(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50)):
    """
    Search SMEs by name.
    
    Query Parameters:
        - q: Search query
        - limit: Max results
    
    Returns:
        List of matching SMEs
    """
    try:
        smes = await portfolio_service.search_smes(q, limit=limit)
        return {"query": q, "results": smes, "count": len(smes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Scenario endpoints
@app.post("/api/v1/scenarios/run")
async def run_scenario(request: ScenarioRequest):
    """
    Run a stress test scenario.
    
    Request Body:
        {
            "scenario_type": "interest_rate" | "sector_shock" | "recession" | "regulation",
            "parameters": {
                // Scenario-specific parameters
                // For interest_rate: {"rate_increase_bps": 200}
                // For sector_shock: {"sector": "Retail/Fashion", "revenue_impact_pct": -20}
                // For recession: {"severity": "moderate", "duration_months": 12}
                // For regulation: {"regulation": "...", "affected_sectors": [...], "revenue_at_risk_pct": 40}
            }
        }
    
    Returns:
        Scenario impact analysis with affected SMEs
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/scenarios/templates")
async def get_scenario_templates():
    """
    Get available scenario templates with parameter descriptions.
    
    Returns:
        List of scenario templates
    """
    templates = [
        {
            "scenario_type": "interest_rate",
            "name": "Interest Rate Shock",
            "description": "Simulate impact of interest rate increase on debt service",
            "parameters": {
                "rate_increase_bps": {
                    "type": "number",
                    "description": "Interest rate increase in basis points",
                    "default": 200,
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
            "description": "Simulate broad economic downturn",
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

# Chat endpoint
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    Process chat via ADK Orchestrator (if enabled) or fallback to rule-based
    """
    try:
        # Try orchestrator first
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                orch_response = await client.post(
                    "http://localhost:8080/orchestrate",
                    json={
                        "message": request.query,
                        "session_id": "default"
                    }
                )
                if orch_response.status_code == 200:
                    data = orch_response.json()
                    return {"answer": data["response"], "type": "adk_orchestrator"}
            except:
                pass  # Fallback to rule-based
        
        # Fallback to existing chat service
        response = await chat_service.process_query(
            request.query,
            use_claude_api=request.use_claude_api
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/chat/history")
async def clear_chat_history():
    """Clear chat conversation history."""
    chat_service.clear_history()
    return {"message": "Chat history cleared"}

# Risk calculation endpoints
@app.get("/api/v1/risk/calculate/{sme_id}")
async def calculate_risk(sme_id: str):
    """
    Calculate comprehensive risk score for an SME.
    
    Path Parameters:
        - sme_id: SME identifier
    
    Returns:
        Risk analysis with component breakdown and default probability
    """
    try:
        risk_analysis = await risk_engine.calculate_risk_score(sme_id)
        return risk_analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/risk/batch")
async def calculate_batch_risk(sme_ids: List[str]):
    """
    Calculate risk scores for multiple SMEs.
    
    Request Body:
        ["0142", "0287", "0531", ...]
    
    Returns:
        List of risk analyses
    """
    try:
        results = await risk_engine.batch_calculate_risk_scores(sme_ids)
        return {"results": results, "count": len(results)}
    except Exception as e:
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
