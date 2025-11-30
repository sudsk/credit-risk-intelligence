"""SME data models"""
from pydantic import BaseModel, Field
from typing import Literal, List
from datetime import datetime


class SME(BaseModel):
    """SME entity"""
    id: str = Field(..., description="SME ID (e.g., #0142)")
    name: str = Field(..., description="SME name")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_category: Literal["critical", "medium", "stable"] = Field(
        ..., description="Risk category"
    )
    exposure: str = Field(..., description="Exposure amount (e.g., €250K)")
    sector: str = Field(..., description="Business sector")
    geography: str = Field(..., description="Geographic region")
    trend: Literal["up", "down", "stable"] = Field(..., description="Risk trend")
    trend_value: int = Field(..., description="Trend change value")


class PortfolioMetrics(BaseModel):
    """Portfolio-level metrics"""
    total_smes: int = Field(..., description="Total SMEs in portfolio")
    total_exposure: str = Field(..., description="Total exposure amount")
    avg_risk_score: int = Field(..., ge=0, le=100, description="Average risk score")
    critical_count: int = Field(..., description="Number of critical SMEs")
    medium_count: int = Field(..., description="Number of medium risk SMEs")
    stable_count: int = Field(..., description="Number of stable SMEs")
    default_probability: float = Field(..., description="Portfolio default probability %")
    portfolio_trend: Literal["up", "down", "stable"] = Field(
        ..., description="Overall portfolio trend"
    )


class SectorBreakdown(BaseModel):
    """Sector breakdown"""
    icon: str
    name: str
    smes: int
    exposure: str
    percent: str


class GeographyBreakdown(BaseModel):
    """Geography breakdown"""
    icon: str
    name: str
    smes: int
    exposure: str
    percent: str


class BreakdownData(BaseModel):
    """Detailed breakdown data"""
    title: str
    total: dict
    sectors: List[SectorBreakdown]
    geographies: List[GeographyBreakdown]
