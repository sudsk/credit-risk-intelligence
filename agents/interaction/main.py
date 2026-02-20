"""
FastAPI server for Interaction Agents
Exposes the Master Orchestrator as the primary endpoint
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.orchestrator.agent import MasterOrchestrator
from agents.shared.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = get_config()
orchestrator: MasterOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise agents on startup, clean up on shutdown"""
    global orchestrator
    logger.info("Initialising Master Orchestrator...")
    orchestrator = MasterOrchestrator()
    logger.info("Master Orchestrator ready")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Credit Risk Interaction API",
    description="SME Credit Risk AI Assistant",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Request / Response Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


class AnalyseRequest(BaseModel):
    sme_id: str


class AnalyseResponse(BaseModel):
    sme_id: str
    analysis: str


class ScenarioRequest(BaseModel):
    description: str


class ScenarioResponse(BaseModel):
    description: str
    analysis: str
    status: str


# --- Endpoints ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """General chat — routed through Master Orchestrator"""
    try:
        response_text = await orchestrator.process(
            request.message,
            session_id=request.session_id,
        )
        return ChatResponse(response=response_text, session_id=request.session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse_sme(request: AnalyseRequest):
    """Deep dive analysis of a specific SME"""
    try:
        analysis = await orchestrator.sme_agent.analyze(request.sme_id)
        return AnalyseResponse(sme_id=request.sme_id, analysis=analysis)
    except Exception as e:
        logger.error(f"SME analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    """Run a what-if scenario simulation"""
    try:
        result = await orchestrator.scenario_agent.simulate(request.description)
        return ScenarioResponse(
            description=result["description"],
            analysis=result.get("analysis", ""),
            status=result.get("status", "completed"),
        )
    except Exception as e:
        logger.error(f"Scenario error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agents": {
            "orchestrator": orchestrator is not None,
            "chat": orchestrator is not None and orchestrator.chat_agent is not None,
            "scenario": orchestrator is not None and orchestrator.scenario_agent is not None,
            "sme": orchestrator is not None and orchestrator.sme_agent is not None,
        },
        "config": {
            "project": config.project_id,
            "location": config.location,
            "model": config.model_name,
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)