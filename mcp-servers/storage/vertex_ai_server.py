"""
Vertex AI MCP Server - Mock Implementation
Provides ML model inference for risk scoring
"""
from fastmcp import FastMCP
from typing import Dict, Any, List
from datetime import datetime
import random

from mcp_servers.shared.mock_data import mock_data

mcp = FastMCP("Vertex AI ML Server")


@mcp.tool()
async def predict_risk_score(
    sme_id: str,
    scenario_parameters: dict
) -> dict:
    """
    Predict risk score under scenario conditions
    
    Args:
        sme_id: SME identifier
        scenario_parameters: Scenario parameters affecting risk
        
    Returns:
        Predicted risk score and confidence
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    current_score = sme["risk_score"]
    
    # Mock scenario impact calculation
    impact = scenario_parameters.get("expected_impact", 0)
    rate_change = scenario_parameters.get("rate_change", 0)
    
    # Interest rate scenarios
    if rate_change != 0:
        # Higher rates = higher risk for companies with debt
        impact = rate_change * 8  # 1% rate = +8 risk points
    
    # Regulation scenarios
    if scenario_parameters.get("regulation_type") == "product_ban":
        impact = 15  # Significant impact
    
    new_score = min(100, max(0, current_score + int(impact)))
    
    return {
        "sme_id": f"#{sme['id']}",
        "current_score": current_score,
        "predicted_score": new_score,
        "change": new_score - current_score,
        "confidence": 0.85,
        "model_version": "risk_score_v3.2",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def get_risk_drivers(sme_id: str) -> dict:
    """
    Get top risk drivers from ML model explainability
    
    Args:
        sme_id: SME identifier
        
    Returns:
        Top risk drivers with SHAP values
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    # Mock risk drivers based on SME characteristics
    drivers = []
    
    # TechStart specific drivers
    if sme["id"] == "0142":
        drivers = [
            {
                "driver": "CTO Departure",
                "impact": 6,
                "direction": "increase",
                "confidence": 0.92,
                "source": "linkedin_data"
            },
            {
                "driver": "Web Traffic Decline (-42% QoQ)",
                "impact": 5,
                "direction": "increase",
                "confidence": 0.88,
                "source": "google_analytics"
            },
            {
                "driver": "Client Loss (2 major)",
                "impact": 3,
                "direction": "increase",
                "confidence": 0.85,
                "source": "crm_data"
            }
        ]
    
    # GreenLeaf specific drivers
    elif sme["id"] == "0445":
        drivers = [
            {
                "driver": "Regulatory Risk (Hemp Ban)",
                "impact": 12,
                "direction": "increase",
                "confidence": 0.75,
                "source": "regulatory_monitoring"
            },
            {
                "driver": "Revenue Concentration",
                "impact": 4,
                "direction": "increase",
                "confidence": 0.80,
                "source": "financial_data"
            }
        ]
    
    # Generic drivers
    else:
        drivers = [
            {
                "driver": "Debt Service Coverage",
                "impact": random.randint(2, 5),
                "direction": "increase" if random.random() > 0.5 else "decrease",
                "confidence": 0.82,
                "source": "financial_data"
            },
            {
                "driver": "Sector Health",
                "impact": random.randint(1, 4),
                "direction": "increase" if random.random() > 0.6 else "decrease",
                "confidence": 0.78,
                "source": "sector_analysis"
            }
        ]
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "current_score": sme["risk_score"],
        "top_drivers": drivers,
        "model_version": "risk_explainer_v2.1",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def predict_default_probability(sme_id: str, horizon_months: int = 12) -> dict:
    """
    Predict probability of default over time horizon
    
    Args:
        sme_id: SME identifier
        horizon_months: Prediction horizon in months
        
    Returns:
        Default probability estimates
    """
    sme = mock_data.get_sme_by_id(sme_id)
    
    if not sme:
        return {"error": f"SME {sme_id} not found"}
    
    # Mock PD calculation based on risk score
    risk_score = sme["risk_score"]
    
    # Higher score = higher PD
    if risk_score >= 80:
        pd_12m = random.uniform(8.0, 15.0)
    elif risk_score >= 50:
        pd_12m = random.uniform(2.0, 8.0)
    else:
        pd_12m = random.uniform(0.1, 2.0)
    
    return {
        "sme_id": f"#{sme['id']}",
        "sme_name": sme["name"],
        "pd_12m": round(pd_12m, 2),
        "pd_24m": round(pd_12m * 1.6, 2),
        "pd_36m": round(pd_12m * 2.1, 2),
        "confidence_interval": {
            "lower": round(pd_12m * 0.7, 2),
            "upper": round(pd_12m * 1.3, 2)
        },
        "model_version": "pd_model_v4.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
async def batch_score_portfolio(sme_ids: List[str]) -> List[dict]:
    """
    Batch score multiple SMEs efficiently
    
    Args:
        sme_ids: List of SME identifiers
        
    Returns:
        List of risk scores
    """
    results = []
    
    for sme_id in sme_ids:
        sme = mock_data.get_sme_by_id(sme_id)
        if sme:
            results.append({
                "sme_id": f"#{sme['id']}",
                "risk_score": sme["risk_score"],
                "risk_category": sme["risk_category"]
            })
    
    return results
