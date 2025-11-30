"""News & Events data models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class PredictedEvent(BaseModel):
    """Predicted future event"""
    id: str = Field(..., description="Event ID")
    date: str = Field(..., description="Predicted date")
    days_until: int = Field(..., description="Days until event")
    title: str = Field(..., description="Event title")
    probability: int = Field(..., ge=0, le=100, description="Probability %")
    affects: dict = Field(..., description="Affected SMEs and exposure")
    impact: str = Field(..., description="Expected impact")
    key_smes: Optional[List[str]] = Field(None, description="Key affected SMEs")
    source: str = Field(..., description="Data source")
    description: str = Field(..., description="Event description")


class NewsItem(BaseModel):
    """News intelligence item"""
    id: str = Field(..., description="News ID")
    timestamp: str = Field(..., description="Detection timestamp")
    sme_id: str = Field(..., description="Related SME ID")
    sme_name: str = Field(..., description="Related SME name")
    exposure: str = Field(..., description="SME exposure")
    type: Literal["departure", "payment_delay", "churn", "other"] = Field(
        ..., description="News type"
    )
    severity: Literal["critical", "warning", "info"] = Field(..., description="Severity")
    title: str = Field(..., description="News headline")
    summary: str = Field(..., description="News summary")
    signals: List[dict] = Field(..., description="Data signals")
    recommendation: str = Field(..., description="AI recommendation")
