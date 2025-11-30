"""Activity data models"""
from pydantic import BaseModel, Field
from typing import Literal


class Activity(BaseModel):
    """System activity"""
    id: str = Field(..., description="Activity ID")
    timestamp: str = Field(..., description="Activity timestamp")
    type: Literal["alert", "info", "success", "warning"] = Field(
        ..., description="Activity type"
    )
    message: str = Field(..., description="Activity message")
