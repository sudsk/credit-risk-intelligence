"""
LinkedIn MCP Server - Mock Implementation
Provides employee data via FastMCP
"""
from fastmcp import FastMCP
from typing import List, Optional
from datetime import datetime, timedelta

from mcp_servers.shared.mock_data import mock_data

# Initialize FastMCP server
mcp = FastMCP("LinkedIn Data Server")


@mcp.tool()
async def get_employee_count(sme_id: str) -> dict:
    """
    Get current employee count for SME
    
    Args:
        sme_id: SME identifier (e.g., "0142" or "#0142")
        
    Returns:
        Employee count and trend data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "employee_count": sme["employee_count"],
        "trend": sme["employee_trend"],
        "change_30d": -5 if sme["employee_trend"] == "down" else 2,
        "source": "linkedin_api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_recent_departures(sme_id: str, days: int = 30) -> List[dict]:
    """
    Get employees who left in last N days
    
    Args:
        sme_id: SME identifier
        days: Number of days to look back (default: 30)
        
    Returns:
        List of employee departure events
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return []
    
    # Mock data for TechStart (0142)
    if sme["id"] == "0142":
        return [
            {
                "employee_id": "emp_001",
                "name": "Sarah Johnson",
                "title": "Chief Technology Officer",
                "joined_date": "2019-03-15",
                "left_date": "2024-11-14",
                "tenure_months": 68,
                "detected_at": "2024-11-14T09:23:17Z",
                "signal": "Profile updated: 'Open to new opportunities'"
            },
            {
                "employee_id": "emp_002",
                "name": "Mike Chen",
                "title": "VP Sales",
                "joined_date": "2020-01-10",
                "left_date": "2024-11-05",
                "tenure_months": 58,
                "detected_at": "2024-11-05T14:12:43Z",
                "signal": "Moved to competitor (LinkedIn update)"
            }
        ]
    
    # Mock data for Digital Marketing Hub (0531)
    elif sme["id"] == "0531":
        return [
            {
                "employee_id": "emp_101",
                "name": "Jessica Williams",
                "title": "Account Manager",
                "joined_date": "2021-06-01",
                "left_date": "2024-10-28",
                "tenure_months": 40,
                "detected_at": "2024-10-28T11:45:22Z",
                "signal": "Profile updated: new role at different company"
            },
            {
                "employee_id": "emp_102",
                "name": "David Brown",
                "title": "Senior Account Manager",
                "joined_date": "2020-09-15",
                "left_date": "2024-11-08",
                "tenure_months": 50,
                "detected_at": "2024-11-08T16:33:11Z",
                "signal": "Profile updated: freelance consultant"
            }
        ]
    
    return []


@mcp.tool()
async def get_job_postings(sme_id: str) -> dict:
    """
    Get current job postings for SME
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Active job postings
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    # TechStart has no replacement postings (red flag)
    if sme["id"] == "0142":
        return {
            "sme_id": f"#{sme['id']}",
            "sme_name": sme["name"],
            "active_postings": 0,
            "recent_postings": [],
            "signal": "⚠️ No replacement hires detected for CTO/VP Sales",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Default mock
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "active_postings": 3,
        "recent_postings": [
            "Software Engineer",
            "Account Manager",
            "Marketing Specialist"
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.resource("sme://linkedin/{sme_id}")
async def get_linkedin_profile(sme_id: str) -> dict:
    """
    Get full LinkedIn company profile for SME
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Complete LinkedIn profile data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "company_name": sme["name"],
        "employee_count": sme["employee_count"],
        "employee_trend": sme["employee_trend"],
        "followers": sme["employee_count"] * 15,  # Mock: ~15 followers per employee
        "recent_activity": [
            {
                "type": "post",
                "date": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
                "engagement": "low"
            }
        ],
        "source": "linkedin_api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
