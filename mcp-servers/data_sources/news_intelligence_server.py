"""
News Intelligence MCP Server - Mock Implementation
Aggregates news and sentiment for SMEs
"""
from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import List

from mcp_servers.shared.mock_data import mock_data

mcp = FastMCP("News Intelligence Server")


@mcp.tool()
async def get_sme_news(sme_id: str, days: int = 30) -> List[dict]:
    """
    Get news and intelligence for SME
    
    Args:
        sme_id: SME identifier
        days: Number of days to look back
        
    Returns:
        List of news items
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return []
    
    # TechStart news
    if sme["id"] == "0142":
        return [
            {
                "id": "news_001",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                "type": "departure",
                "severity": "critical",
                "title": "CTO Departure Detected",
                "summary": "LinkedIn shows CTO Sarah Johnson departed 2 hours ago. No replacement detected.",
                "signals": [
                    {"source": "LinkedIn", "detail": "CTO profile updated"},
                    {"source": "Web Traffic", "detail": "-42% QoQ decline"},
                    {"source": "Client Data", "detail": "2 major clients lost"}
                ],
                "recommendation": "Immediate management meeting recommended"
            }
        ]
    
    # GreenLeaf news
    elif sme["id"] == "0445":
        return [
            {
                "id": "news_002",
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "type": "regulation",
                "severity": "warning",
                "title": "Potential Hemp Ban Impact",
                "summary": "Parliamentary vote on hemp products ban scheduled for Dec 1. 75% probability.",
                "signals": [
                    {"source": "Parliament Calendar", "detail": "Vote scheduled"},
                    {"source": "Committee Reports", "detail": "Strong support for ban"}
                ],
                "recommendation": "Prepare contingency plan for revenue diversification"
            }
        ]
    
    return []


@mcp.tool()
async def get_sentiment_analysis(sme_id: str) -> dict:
    """
    Get sentiment analysis from various sources
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Aggregated sentiment data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    # Digital Marketing Hub has declining sentiment
    if sme["id"] == "0531":
        return {
            "sme_id": f"#{sme['id']}",
            "sme_name": sme["name"],
            "overall_sentiment": "negative",
            "sentiment_score": -0.42,
            "sources": {
                "trustpilot": {
                    "score": 3.1,
                    "trend": "declining",
                    "change": -1.1
                },
                "google_reviews": {
                    "score": 3.4,
                    "trend": "declining",
                    "change": -0.8
                },
                "glassdoor": {
                    "score": 2.9,
                    "trend": "stable",
                    "change": 0.0
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Default positive sentiment
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "overall_sentiment": "positive",
        "sentiment_score": 0.65,
        "sources": {
            "trustpilot": {"score": 4.2, "trend": "stable"},
            "google_reviews": {"score": 4.3, "trend": "improving"}
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
