#!/usr/bin/env python3
"""
Companies House MCP Server
Provides official company registration, director changes, and compliance data.
In production, this would connect to Companies House API.
"""

import asyncio
import pandas as pd
from datetime import datetime
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
COMPANIES_CSV = DATA_DIR / "company_info.csv"

# Load data
companies_df = pd.read_csv(COMPANIES_CSV)

# Create MCP server
server = Server("companies-house-data")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Companies House tools."""
    return [
        Tool(
            name="get_company_info",
            description="Get official company registration details and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "sme_id": {
                        "type": "string",
                        "description": "SME identifier"
                    }
                },
                "required": ["sme_id"]
            }
        ),
        Tool(
            name="check_compliance_status",
            description="Check regulatory compliance, overdue accounts, and CCJs",
            inputSchema={
                "type": "object",
                "properties": {
                    "sme_id": {
                        "type": "string",
                        "description": "SME identifier"
                    }
                },
                "required": ["sme_id"]
            }
        ),
        Tool(
            name="get_director_changes",
            description="Get director changes in the last 12 months",
            inputSchema={
                "type": "object",
                "properties": {
                    "sme_id": {
                        "type": "string",
                        "description": "SME identifier"
                    }
                },
                "required": ["sme_id"]
            }
        ),
        Tool(
            name="assess_corporate_health",
            description="Overall corporate health assessment from regulatory perspective",
            inputSchema={
                "type": "object",
                "properties": {
                    "sme_id": {
                        "type": "string",
                        "description": "SME identifier"
                    }
                },
                "required": ["sme_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    sme_id = arguments.get("sme_id")
    
    if name == "get_company_info":
        company_row = companies_df[companies_df['sme_id'] == sme_id]
        
        if company_row.empty:
            return [TextContent(
                type="text",
                text=f"No company data found for SME {sme_id}"
            )]
        
        data = company_row.iloc[0]
        
        info = {
            "sme_id": sme_id,
            "company_number": data['company_number'],
            "company_status": data['company_status'],
            "incorporation_date": data['incorporation_date'],
            "registered_address_postcode": data['registered_address_postcode'],
            "sic_code": data['sic_code'],
            "director_count": int(data['director_count']),
            "last_accounts_date": data['last_accounts_date'],
            "next_accounts_due": data['next_accounts_due'],
            "last_updated": data['last_updated']
        }
        
        return [TextContent(
            type="text",
            text=f"Company Information:\n{pd.Series(info).to_string()}"
        )]
    
    elif name == "check_compliance_status":
        company_row = companies_df[companies_df['sme_id'] == sme_id]
        
        if company_row.empty:
            return [TextContent(
                type="text",
                text=f"No compliance data found for SME {sme_id}"
            )]
        
        data = company_row.iloc[0]
        
        # Check if accounts are overdue
        next_due = pd.to_datetime(data['next_accounts_due'])
        is_overdue = next_due < datetime.now()
        days_overdue = (datetime.now() - next_due).days if is_overdue else 0
        
        insolvency = bool(data['insolvency_flag'])
        ccj_count = int(data['ccj_count'])
        
        compliance = {
            "sme_id": sme_id,
            "accounts_overdue": is_overdue,
            "days_overdue": days_overdue if is_overdue else 0,
            "next_accounts_due": data['next_accounts_due'],
            "ccj_count": ccj_count,
            "insolvency_flag": insolvency,
            "compliance_status": _assess_compliance(is_overdue, days_overdue, ccj_count, insolvency),
            "risk_level": _compliance_risk_level(is_overdue, days_overdue, ccj_count, insolvency)
        }
        
        return [TextContent(
            type="text",
            text=f"Compliance Status:\n{pd.Series(compliance).to_string()}"
        )]
    
    elif name == "get_director_changes":
        company_row = companies_df[companies_df['sme_id'] == sme_id]
        
        if company_row.empty:
            return [TextContent(
                type="text",
                text=f"No director data found for SME {sme_id}"
            )]
        
        data = company_row.iloc[0]
        director_changes = int(data['director_changes_12m'])
        current_directors = int(data['director_count'])
        
        changes = {
            "sme_id": sme_id,
            "current_director_count": current_directors,
            "director_changes_12m": director_changes,
            "change_rate": round((director_changes / current_directors * 100), 1) if current_directors > 0 else 0,
            "stability_assessment": _assess_director_stability(director_changes, current_directors),
            "risk_impact": _director_change_risk(director_changes)
        }
        
        return [TextContent(
            type="text",
            text=f"Director Changes (12 months):\n{pd.Series(changes).to_string()}"
        )]
    
    elif name == "assess_corporate_health":
        company_row = companies_df[companies_df['sme_id'] == sme_id]
        
        if company_row.empty:
            return [TextContent(
                type="text",
                text=f"No corporate data found for SME {sme_id}"
            )]
        
        data = company_row.iloc[0]
        
        # Calculate composite health score
        next_due = pd.to_datetime(data['next_accounts_due'])
        is_overdue = next_due < datetime.now()
        days_overdue = (datetime.now() - next_due).days if is_overdue else 0
        
        insolvency = bool(data['insolvency_flag'])
        ccj_count = int(data['ccj_count'])
        director_changes = int(data['director_changes_12m'])
        company_status = data['company_status']
        
        # Calculate risk score (0-100, higher = worse)
        health_score = _calculate_corporate_health_score(
            is_overdue, days_overdue, ccj_count, insolvency, 
            director_changes, company_status
        )
        
        assessment = {
            "sme_id": sme_id,
            "corporate_health_score": round(health_score, 1),
            "health_rating": _rate_corporate_health(health_score),
            "company_status": company_status,
            "key_concerns": _identify_corporate_concerns(
                is_overdue, days_overdue, ccj_count, insolvency, director_changes
            ),
            "risk_contribution": f"Adds {_corporate_risk_points(health_score)} points to overall risk score"
        }
        
        concerns_list = ', '.join(assessment['key_concerns']) if assessment['key_concerns'] else 'None'
        
        return [TextContent(
            type="text",
            text=f"Corporate Health Assessment:\n{pd.Series({k: v for k, v in assessment.items() if k != 'key_concerns'}).to_string()}\n\nKey Concerns:\n{concerns_list}"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

def _assess_compliance(overdue: bool, days: int, ccjs: int, insolvency: bool) -> str:
    """Assess compliance status."""
    if insolvency:
        return "🔴 CRITICAL: Insolvency proceedings active"
    elif overdue and days > 90:
        return "🔴 CRITICAL: Accounts severely overdue"
    elif ccjs >= 3:
        return "🟠 HIGH RISK: Multiple County Court Judgements"
    elif overdue and days > 30:
        return "🟡 WARNING: Accounts overdue"
    elif ccjs > 0:
        return "⚠️ CAUTION: CCJ on record"
    else:
        return "✅ COMPLIANT: All filings up to date"

def _compliance_risk_level(overdue: bool, days: int, ccjs: int, insolvency: bool) -> str:
    """Determine compliance risk level."""
    if insolvency:
        return "CRITICAL"
    elif (overdue and days > 90) or ccjs >= 3:
        return "HIGH"
    elif (overdue and days > 30) or ccjs >= 2:
        return "MEDIUM"
    elif overdue or ccjs > 0:
        return "LOW"
    else:
        return "MINIMAL"

def _assess_director_stability(changes: int, current: int) -> str:
    """Assess director stability."""
    if current == 0:
        return "🔴 CRITICAL: No directors on record"
    
    change_rate = (changes / current * 100) if current > 0 else 0
    
    if change_rate > 50:
        return "🔴 CRITICAL: High director turnover (>50%)"
    elif changes >= 3:
        return "🟠 WARNING: Multiple director changes"
    elif changes >= 2:
        return "🟡 CAUTION: Some director changes"
    elif changes == 1:
        return "⚠️ WATCH: One director change"
    else:
        return "✅ STABLE: No director changes"

def _director_change_risk(changes: int) -> str:
    """Calculate risk impact from director changes."""
    if changes >= 4:
        return "Adds 20 points to risk score"
    elif changes == 3:
        return "Adds 15 points to risk score"
    elif changes == 2:
        return "Adds 10 points to risk score"
    elif changes == 1:
        return "Adds 5 points to risk score"
    else:
        return "No additional risk"

def _calculate_corporate_health_score(overdue: bool, days: int, ccjs: int, 
                                     insolvency: bool, dir_changes: int, status: str) -> float:
    """Calculate corporate health score (0=excellent, 100=critical)."""
    score = 10  # Base score
    
    # Company status
    if status != "Active":
        score += 80
        return min(score, 100)
    
    # Insolvency flag
    if insolvency:
        score += 90
        return min(score, 100)
    
    # Overdue accounts
    if overdue:
        if days > 180:
            score += 70
        elif days > 90:
            score += 50
        elif days > 30:
            score += 30
        else:
            score += 15
    
    # CCJs
    score += ccjs * 15
    
    # Director changes
    if dir_changes >= 4:
        score += 20
    elif dir_changes >= 3:
        score += 15
    elif dir_changes >= 2:
        score += 10
    elif dir_changes == 1:
        score += 5
    
    return min(score, 100)

def _rate_corporate_health(score: float) -> str:
    """Rate corporate health."""
    if score < 20:
        return "Excellent (Minimal Risk)"
    elif score < 35:
        return "Good (Low Risk)"
    elif score < 50:
        return "Fair (Medium Risk)"
    elif score < 70:
        return "Poor (High Risk)"
    else:
        return "Critical (Very High Risk)"

def _identify_corporate_concerns(overdue: bool, days: int, ccjs: int, 
                                insolvency: bool, dir_changes: int) -> list[str]:
    """Identify corporate concerns."""
    concerns = []
    
    if insolvency:
        concerns.append("Active insolvency proceedings")
    
    if overdue:
        if days > 90:
            concerns.append(f"Accounts severely overdue ({days} days)")
        else:
            concerns.append(f"Accounts overdue ({days} days)")
    
    if ccjs >= 3:
        concerns.append(f"Multiple CCJs ({ccjs})")
    elif ccjs > 0:
        concerns.append(f"{ccjs} County Court Judgement(s)")
    
    if dir_changes >= 3:
        concerns.append(f"Frequent director changes ({dir_changes} in 12m)")
    elif dir_changes >= 2:
        concerns.append(f"Multiple director changes ({dir_changes} in 12m)")
    
    return concerns

def _corporate_risk_points(health_score: float) -> str:
    """Map corporate health to risk points."""
    if health_score < 25:
        return "5-10"
    elif health_score < 40:
        return "10-20"
    elif health_score < 60:
        return "20-35"
    elif health_score < 80:
        return "35-50"
    else:
        return "50-70"

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())