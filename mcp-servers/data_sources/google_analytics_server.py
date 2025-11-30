"""
Google Analytics MCP Server - Mock Implementation
Provides web traffic and engagement data
"""
from fastmcp import FastMCP
from datetime import datetime, timedelta
import random

from mcp_servers.shared.mock_data import mock_data

mcp = FastMCP("Google Analytics Server")


@mcp.tool()
async def get_traffic_metrics(sme_id: str, days: int = 90) -> dict:
    """
    Get web traffic metrics for SME
    
    Args:
        sme_id: SME identifier
        days: Number of days to analyze
        
    Returns:
        Traffic metrics and trends
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    # Mock traffic data
    base_traffic = random.randint(5000, 50000)
    
    # TechStart has declining traffic
    if sme["id"] == "0142":
        return {
            "sme_id": f"#{sme['id']}",
            "sme_name": sme["name"],
            "period_days": days,
            "total_sessions": 18500,
            "total_users": 12300,
            "avg_session_duration": "2m 15s",
            "bounce_rate": "58.2%",
            "trend": {
                "sessions_change_qoq": -42.0,
                "users_change_qoq": -38.5,
                "direction": "declining"
            },
            "signal": "⚠️ Significant traffic decline",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Generic SME
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "period_days": days,
        "total_sessions": base_traffic,
        "total_users": int(base_traffic * 0.65),
        "avg_session_duration": "3m 42s",
        "bounce_rate": "45.8%",
        "trend": {
            "sessions_change_qoq": random.uniform(-10, 15),
            "users_change_qoq": random.uniform(-8, 12),
            "direction": "stable"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_conversion_metrics(sme_id: str) -> dict:
    """
    Get conversion and engagement metrics
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Conversion data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "conversion_rate": round(random.uniform(1.5, 5.0), 2),
        "avg_order_value": f"€{random.randint(50, 500)}",
        "cart_abandonment_rate": round(random.uniform(60, 80), 1),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_traffic_sources(sme_id: str) -> dict:
    """
    Get traffic source breakdown
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Traffic source data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "sources": {
            "organic": 45.2,
            "direct": 28.5,
            "social": 15.8,
            "paid": 7.3,
            "referral": 3.2
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
