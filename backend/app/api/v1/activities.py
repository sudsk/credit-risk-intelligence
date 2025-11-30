"""
Activities API endpoints
"""
from fastapi import APIRouter
from typing import List
from app.models.activity import Activity
from app.services.activity_service import ActivityService

router = APIRouter()
activity_service = ActivityService()


@router.get("/", response_model=List[Activity])
async def get_activities():
    """Get system activities"""
    return activity_service.get_all_activities()
