"""
BigQuery MCP Server - Mock Implementation
Provides portfolio data and analytics
"""
from fastmcp import FastMCP
from typing import List, Dict, Any
from datetime import datetime

from mcp_servers.shared.mock_data import mock_data

mcp = FastMCP("BigQuery Data Server")


@mcp.tool()
async def get_sme_data(sme_id: str) -> dict:
    """
    Get comprehensive SME data from BigQuery
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Complete SME record
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "name": sme["name"],
        "risk_score": sme["risk_score"],
        "risk_category": sme["risk_category"],
        "exposure": sme["exposure"],
        "sector": sme["sector"],
        "geography": sme["geography"],
        "financials": {
            "revenue": sme["revenue"],
            "ebitda": sme["ebitda"],
            "debt_service_coverage": "1.8x",
            "cash_reserves": "€180K"
        },
        "employee_count": sme["employee_count"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_portfolio_metrics() -> dict:
    """
    Get portfolio-level metrics
    
    Returns:
        Aggregated portfolio statistics
    """
    all_smes = mock_data.get_all_smes()
    
    critical = [s for s in all_smes if s["risk_category"] == "critical"]
    medium = [s for s in all_smes if s["risk_category"] == "medium"]
    stable = [s for s in all_smes if s["risk_category"] == "stable"]
    
    return {
        "total_smes": 1284,  # Mock: actual would be larger
        "total_exposure": "€328M",
        "avg_risk_score": 64,
        "critical": {
            "count": 23,
            "exposure": "€42M",
            "percent": 12.8
        },
        "medium": {
            "count": 142,
            "exposure": "€98M",
            "percent": 29.9
        },
        "stable": {
            "count": 1119,
            "exposure": "€188M",
            "percent": 57.3
        },
        "default_probability": 2.8,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def filter_smes_by_criteria(
    scenario_type: str,
    parameters: dict
) -> List[str]:
    """
    Filter SMEs by scenario criteria
    
    Args:
        scenario_type: Type of scenario
        parameters: Scenario parameters
        
    Returns:
        List of affected SME IDs
    """
    all_smes = mock_data.get_all_smes()
    
    # Mock filtering logic
    if scenario_type == "interest_rate":
        # SMEs with high debt loads (mock: ~38% of portfolio)
        return [f"#{s['id']}" for s in all_smes[:19]]  # Mock: would be ~487 SMEs
    
    elif scenario_type == "regulation":
        # Sector-specific
        sector = parameters.get("affected_sector", "Food/Hospitality")
        filtered = [s for s in all_smes if s["sector"] == sector]
        return [f"#{s['id']}" for s in filtered]
    
    elif scenario_type == "sector_shock":
        sector = parameters.get("sector")
        filtered = [s for s in all_smes if s["sector"] == sector]
        return [f"#{s['id']}" for s in filtered]
    
    else:
        # Generic: return some SMEs
        return [f"#{s['id']}" for s in all_smes[:10]]


@mcp.tool()
async def get_sme_financials(sme_id: str) -> dict:
    """
    Get detailed financial metrics for SME
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Financial metrics and trends
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "revenue": sme["revenue"],
        "revenue_growth_yoy": "5.2%",
        "revenue_growth_qoq": "-2.8%",
        "ebitda": sme["ebitda"],
        "ebitda_margin": "17.5%",
        "debt_service_coverage": "1.8x",
        "current_ratio": "1.4",
        "quick_ratio": "1.1",
        "cash_reserves": "€180K",
        "total_debt": "€420K",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_peer_comparison(sme_id: str) -> dict:
    """
    Compare SME to sector peers
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Peer comparison data
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "sector": sme["sector"],
        "metrics": {
            "risk_score": {
                "this_sme": sme["risk_score"],
                "peer_avg": 55,
                "peer_median": 52,
                "percentile": "75th"
            },
            "revenue_growth": {
                "this_sme": "5.2%",
                "peer_avg": "8.5%",
                "peer_median": "7.2%",
                "percentile": "40th"
            },
            "ebitda_margin": {
                "this_sme": "17.5%",
                "peer_avg": "15.2%",
                "peer_median": "14.8%",
                "percentile": "65th"
            }
        },
        "peer_count": 28,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
