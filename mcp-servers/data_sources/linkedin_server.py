#!/usr/bin/env python3
"""
LinkedIn Data MCP Server - Cloud Run Compatible
Provides employee count, hiring trends, and departure data from CSV files.
"""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastmcp import FastMCP

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
EMPLOYEES_CSV = DATA_DIR / "employees.csv"
DEPARTURES_CSV = DATA_DIR / "departures.csv"

# Load data
employees_df = pd.read_csv(EMPLOYEES_CSV)
departures_df = pd.read_csv(DEPARTURES_CSV)

# Create FastMCP server
mcp = FastMCP("linkedin-data")


@mcp.tool()
def get_employee_count(sme_id: str) -> dict:
    """Get current employee count and hiring trends for an SME"""
    emp_row = employees_df[employees_df['sme_id'] == sme_id]
    
    if emp_row.empty:
        return {"error": f"No employee data found for SME {sme_id}"}
    
    emp_data = emp_row.iloc[0]
    
    result = {
        "sme_id": sme_id,
        "current_employee_count": int(emp_data['employee_count']),
        "trend": emp_data['trend'],
        "change_30d": int(emp_data['change_30d']),
        "change_90d": int(emp_data['change_90d']),
        "hiring_active": bool(emp_data['hiring_active']),
        "last_updated": emp_data['last_updated']
    }
    
    return result


@mcp.tool()
def get_employee_trend(sme_id: str) -> dict:
    """Get employee growth/decline trend over 30 and 90 days"""
    emp_row = employees_df[employees_df['sme_id'] == sme_id]
    
    if emp_row.empty:
        return {"error": f"No trend data found for SME {sme_id}"}
    
    emp_data = emp_row.iloc[0]
    current = int(emp_data['employee_count'])
    change_30d = int(emp_data['change_30d'])
    change_90d = int(emp_data['change_90d'])
    
    # Calculate historical counts
    count_30d_ago = current - change_30d
    count_90d_ago = current - change_90d
    
    trend_analysis = {
        "current_count": current,
        "count_30_days_ago": count_30d_ago,
        "count_90_days_ago": count_90d_ago,
        "change_30d": change_30d,
        "change_90d": change_90d,
        "pct_change_30d": round((change_30d / count_30d_ago * 100), 1) if count_30d_ago > 0 else 0,
        "pct_change_90d": round((change_90d / count_90d_ago * 100), 1) if count_90d_ago > 0 else 0,
        "trend_direction": emp_data['trend'],
        "interpretation": _interpret_employee_trend(change_30d, change_90d)
    }
    
    return trend_analysis


@mcp.tool()
def get_recent_departures(sme_id: str, days: int = 90) -> dict:
    """Get list of recent employee departures (especially senior staff)"""
    # Filter departures for this SME
    departures = departures_df[departures_df['sme_id'] == sme_id].copy()
    
    if departures.empty:
        return {"info": f"No departures recorded for SME {sme_id} in last {days} days"}
    
    # Parse dates and filter by time window
    departures['left_date'] = pd.to_datetime(departures['left_date'])
    cutoff_date = datetime.now() - pd.Timedelta(days=days)
    recent_departures = departures[departures['left_date'] >= cutoff_date]
    
    if recent_departures.empty:
        return {"info": f"No departures in last {days} days for SME {sme_id}"}
    
    # Format departure summary
    departure_list = []
    for idx, row in recent_departures.iterrows():
        departure_list.append({
            "name": row['employee_name'],
            "title": row['title'],
            "seniority": row['seniority'],
            "tenure_months": int(row['tenure_months']),
            "left_date": row['left_date'].strftime('%Y-%m-%d'),
            "reason": row['reason'],
            "replacement_hired": bool(row['replacement_hired'])
        })
    
    # Calculate risk indicators
    c_level_departures = recent_departures[recent_departures['seniority'] == 'C-Level']
    vp_departures = recent_departures[recent_departures['seniority'] == 'VP']
    unreplaced = recent_departures[recent_departures['replacement_hired'] == False]
    
    summary = {
        "total_departures": len(recent_departures),
        "c_level_departures": len(c_level_departures),
        "vp_departures": len(vp_departures),
        "unreplaced_positions": len(unreplaced),
        "risk_level": _assess_departure_risk(len(c_level_departures), len(vp_departures), len(unreplaced)),
        "departures": departure_list
    }
    
    return summary


@mcp.tool()
def check_hiring_activity(sme_id: str) -> dict:
    """Check if company is actively hiring (indicator of growth)"""
    emp_row = employees_df[employees_df['sme_id'] == sme_id]
    
    if emp_row.empty:
        return {"error": f"No hiring data found for SME {sme_id}"}
    
    emp_data = emp_row.iloc[0]
    is_hiring = bool(emp_data['hiring_active'])
    change_30d = int(emp_data['change_30d'])
    
    hiring_status = {
        "sme_id": sme_id,
        "actively_hiring": is_hiring,
        "recent_hires_30d": max(0, change_30d),  # Only positive changes are hires
        "trend": emp_data['trend'],
        "interpretation": _interpret_hiring(is_hiring, change_30d)
    }
    
    return hiring_status


# Helper functions
def _interpret_employee_trend(change_30d: int, change_90d: int) -> str:
    """Interpret employee trend for risk assessment."""
    if change_90d < -10:
        return "🔴 CRITICAL: Mass layoffs detected (>10 employees in 90d)"
    elif change_90d < -5:
        return "🟠 WARNING: Significant downsizing (5-10 employees in 90d)"
    elif change_30d < -3:
        return "🟡 CAUTION: Recent layoffs detected (>3 in 30d)"
    elif change_90d < 0:
        return "⚠️ WATCH: Slow decline in headcount"
    elif change_90d < 5:
        return "✅ STABLE: Minimal change in headcount"
    else:
        return "🟢 POSITIVE: Growing headcount (hiring)"


def _assess_departure_risk(c_level: int, vp_level: int, unreplaced: int) -> str:
    """Assess risk level from departures."""
    if c_level >= 2 or (c_level >= 1 and vp_level >= 2):
        return "CRITICAL"
    elif c_level >= 1 or vp_level >= 2:
        return "HIGH"
    elif vp_level >= 1 or unreplaced >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def _interpret_hiring(is_hiring: bool, change_30d: int) -> str:
    """Interpret hiring activity."""
    if is_hiring and change_30d > 3:
        return "🟢 POSITIVE: Active hiring indicates growth/expansion"
    elif is_hiring and change_30d > 0:
        return "✅ STABLE: Modest hiring for replacement/growth"
    elif is_hiring:
        return "⚠️ WATCH: Hiring but headcount declining (high turnover?)"
    else:
        return "🔴 WARNING: No active hiring (cost-cutting or limited growth)"


if __name__ == "__main__":
    # Use streamable-http for Cloud Run deployment
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8003))
    )