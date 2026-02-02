#!/usr/bin/env python3
"""
Payment Data MCP Server
Provides payment behavior, delays, and cash flow patterns.
In production, this would connect to Core Banking or Trade Credit Data providers.
"""

import asyncio
import pandas as pd
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
FINANCIAL_CSV = DATA_DIR / "financial_data.csv"

# Load data
financial_df = pd.read_csv(FINANCIAL_CSV)

# Create MCP server
server = Server("payment-data")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available payment data tools."""
    return [
        Tool(
            name="get_payment_behavior",
            description="Get current payment behavior metrics",
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
            name="check_payment_delays",
            description="Check for payment delays and trends",
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
            name="assess_payment_risk",
            description="Overall payment risk assessment",
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
    
    if name == "get_payment_behavior":
        fin_row = financial_df[financial_df['sme_id'] == sme_id]
        
        if fin_row.empty:
            return [TextContent(
                type="text",
                text=f"No payment data found for SME {sme_id}"
            )]
        
        data = fin_row.iloc[0]
        
        payment_days = int(data['payment_days_avg'])
        payment_trend = data['payment_days_trend']
        working_capital = int(data['working_capital'])
        
        behavior = {
            "sme_id": sme_id,
            "avg_payment_days": payment_days,
            "payment_trend": payment_trend,
            "working_capital": f"€{working_capital:,}",
            "payment_rating": _rate_payment_days(payment_days),
            "behavior_assessment": _assess_payment_behavior(payment_days, payment_trend)
        }
        
        return [TextContent(
            type="text",
            text=f"Payment Behavior:\n{pd.Series(behavior).to_string()}"
        )]
    
    elif name == "check_payment_delays":
        fin_row = financial_df[financial_df['sme_id'] == sme_id]
        
        if fin_row.empty:
            return [TextContent(
                type="text",
                text=f"No payment delay data found for SME {sme_id}"
            )]
        
        data = fin_row.iloc[0]
        
        payment_days = int(data['payment_days_avg'])
        payment_trend = data['payment_days_trend']
        
        # Industry standard is 30 days
        delay_days = max(0, payment_days - 30)
        is_delayed = payment_days > 30
        
        delays = {
            "sme_id": sme_id,
            "avg_payment_days": payment_days,
            "industry_standard": 30,
            "delay_vs_standard": delay_days,
            "payment_trend": payment_trend,
            "is_deteriorating": payment_trend == "increasing",
            "delay_severity": _assess_delay_severity(payment_days, payment_trend),
            "risk_signal": _payment_delay_risk_signal(payment_days, payment_trend)
        }
        
        return [TextContent(
            type="text",
            text=f"Payment Delay Analysis:\n{pd.Series(delays).to_string()}"
        )]
    
    elif name == "assess_payment_risk":
        fin_row = financial_df[financial_df['sme_id'] == sme_id]
        
        if fin_row.empty:
            return [TextContent(
                type="text",
                text=f"No payment risk data found for SME {sme_id}"
            )]
        
        data = fin_row.iloc[0]
        
        payment_days = int(data['payment_days_avg'])
        payment_trend = data['payment_days_trend']
        working_capital = int(data['working_capital'])
        cash_runway = float(data['cash_runway_months'])
        
        # Calculate payment risk score
        risk_score = _calculate_payment_risk_score(payment_days, payment_trend, working_capital, cash_runway)
        
        assessment = {
            "sme_id": sme_id,
            "payment_risk_score": round(risk_score, 1),
            "risk_rating": _rate_payment_risk(risk_score),
            "avg_payment_days": payment_days,
            "payment_trend": payment_trend,
            "working_capital": f"€{working_capital:,}",
            "cash_runway_months": round(cash_runway, 1),
            "early_warning_signal": _is_early_warning(payment_days, payment_trend),
            "risk_contribution": f"Adds {_payment_risk_points(risk_score)} points to overall risk score"
        }
        
        return [TextContent(
            type="text",
            text=f"Payment Risk Assessment:\n{pd.Series(assessment).to_string()}"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

def _rate_payment_days(days: int) -> str:
    """Rate payment performance."""
    if days <= 30:
        return "Excellent (On-time)"
    elif days <= 45:
        return "Good (Slightly delayed)"
    elif days <= 60:
        return "Fair (Moderately delayed)"
    elif days <= 90:
        return "Poor (Significantly delayed)"
    else:
        return "Critical (Severely delayed)"

def _assess_payment_behavior(days: int, trend: str) -> str:
    """Assess payment behavior."""
    if trend == "increasing" and days > 45:
        return "🔴 CRITICAL: Payment delays worsening, cash flow crisis likely"
    elif trend == "increasing" and days > 30:
        return "🟠 WARNING: Payment delays increasing, cash flow pressure"
    elif days > 60:
        return "🟡 CONCERN: Significantly delayed payments"
    elif days > 45:
        return "⚠️ WATCH: Elevated payment days"
    elif trend == "decreasing":
        return "🟢 POSITIVE: Payment performance improving"
    else:
        return "✅ HEALTHY: Payment behavior normal"

def _assess_delay_severity(days: int, trend: str) -> str:
    """Assess delay severity."""
    if trend == "increasing":
        if days > 60:
            return "Critical (Delays worsening, >60 days)"
        elif days > 45:
            return "High (Delays worsening, 45-60 days)"
        elif days > 30:
            return "Medium (Delays worsening, 30-45 days)"
        else:
            return "Low (Slight increase)"
    else:
        if days > 60:
            return "High (Consistently delayed, >60 days)"
        elif days > 45:
            return "Medium (Moderately delayed, 45-60 days)"
        elif days > 30:
            return "Low (Slightly delayed, 30-45 days)"
        else:
            return "None (On-time payment)"

def _payment_delay_risk_signal(days: int, trend: str) -> str:
    """Determine if payment delays are an early warning signal."""
    if trend == "increasing" and days > 45:
        return "🚨 STRONG EARLY WARNING: Deteriorating payment behavior signals cash flow crisis (2-4 week lead indicator)"
    elif trend == "increasing":
        return "⚠️ EARLY WARNING: Payment delays increasing (monitor closely)"
    elif days > 60:
        return "🔴 HIGH RISK: Severely delayed payments indicate cash problems"
    else:
        return "✅ LOW RISK: Payment behavior within acceptable range"

def _calculate_payment_risk_score(days: int, trend: str, working_capital: int, cash_runway: float) -> float:
    """Calculate payment risk score (0-100, higher = worse)."""
    score = 10  # Base score
    
    # Payment days
    if days > 90:
        score += 50
    elif days > 60:
        score += 35
    elif days > 45:
        score += 20
    elif days > 30:
        score += 10
    
    # Payment trend
    if trend == "increasing":
        if days > 45:
            score += 25
        elif days > 30:
            score += 15
        else:
            score += 8
    elif trend == "decreasing":
        score -= 5  # Improvement
    
    # Working capital
    if working_capital < 0:
        score += 30
    elif working_capital < 100000:
        score += 15
    
    # Cash runway
    if cash_runway < 3:
        score += 20
    elif cash_runway < 6:
        score += 10
    
    return min(score, 100)

def _rate_payment_risk(score: float) -> str:
    """Rate payment risk."""
    if score < 25:
        return "Low (Good payment behavior)"
    elif score < 40:
        return "Low-Medium (Minor concerns)"
    elif score < 60:
        return "Medium (Notable payment delays)"
    elif score < 75:
        return "High (Significant payment issues)"
    else:
        return "Critical (Severe payment delays)"

def _is_early_warning(days: int, trend: str) -> str:
    """Determine if payment behavior is an early warning signal."""
    if trend == "increasing" and days > 45:
        return "YES - Strong early warning signal (2-4 week lead)"
    elif trend == "increasing" and days > 30:
        return "YES - Moderate early warning signal"
    elif days > 60:
        return "CONCURRENT - Already indicating problems"
    else:
        return "NO - Payment behavior normal"

def _payment_risk_points(score: float) -> str:
    """Map payment risk to risk score points."""
    if score < 30:
        return "5-10"
    elif score < 50:
        return "10-20"
    elif score < 70:
        return "20-40"
    else:
        return "40-55"

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