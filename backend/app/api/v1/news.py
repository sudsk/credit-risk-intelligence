"""
News & Events API endpoints
"""
from fastapi import APIRouter
from typing import List
from app.models.news import PredictedEvent, NewsItem
from app.services.news_service import NewsService

router = APIRouter()
news_service = NewsService()


@router.get("/predicted-events", response_model=List[PredictedEvent])
async def get_predicted_events():
    """Get predicted events (next 90 days)"""
    return news_service.get_predicted_events()


@router.get("/intelligence", response_model=List[NewsItem])
async def get_news_intelligence():
    """Get news intelligence items"""
    return news_service.get_news_intelligence()
