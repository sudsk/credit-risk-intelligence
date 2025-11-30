"""
Portfolio API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.sme import SME, PortfolioMetrics, BreakdownData
from app.services.portfolio_service import PortfolioService

router = APIRouter()
portfolio_service = PortfolioService()


@router.get("/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics():
    """Get portfolio-level metrics"""
    return portfolio_service.get_metrics()


@router.get("/smes", response_model=List[SME])
async def get_smes():
    """Get all SMEs in portfolio"""
    return portfolio_service.get_all_smes()


@router.get("/smes/{sme_id}", response_model=SME)
async def get_sme_by_id(sme_id: str):
    """Get specific SME by ID"""
    sme = portfolio_service.get_sme_by_id(sme_id)
    if not sme:
        raise HTTPException(status_code=404, detail=f"SME {sme_id} not found")
    return sme


@router.get("/breakdown/{risk_level}", response_model=BreakdownData)
async def get_breakdown(risk_level: str):
    """Get breakdown data for risk level"""
    if risk_level not in ["critical", "medium", "stable"]:
        raise HTTPException(status_code=400, detail="Invalid risk level")
    return portfolio_service.get_breakdown_data(risk_level)
