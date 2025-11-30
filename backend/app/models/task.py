"""Task data models"""
from pydantic import BaseModel, Field
from typing import Literal


class Task(BaseModel):
    """Task entity"""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    sme_id: str = Field(..., description="Related SME ID")
    sme_name: str = Field(..., description="Related SME name")
    exposure: str = Field(..., description="SME exposure")
    assignee: str = Field(..., description="Assigned analyst")
    priority: Literal["high", "medium", "low"] = Field(..., description="Task priority")
    due_date: str = Field(..., description="Due date")
    status: Literal["overdue", "due_today", "upcoming", "completed"] = Field(
        ..., description="Task status"
    )
    description: str = Field(..., description="Task description")
    source: str = Field(..., description="Task source")
    created_at: str = Field(..., description="Creation timestamp")
