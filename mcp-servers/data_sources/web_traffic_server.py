#!/usr/bin/env python3
"""
Web Traffic Analytics MCP Server
Provides website traffic, engagement, and digital footprint data from CSV files.
In production, this would connect to SimilarWeb API or Google Analytics.
"""

import asyncio
import pandas as pd
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
TRAFFIC_CSV = DATA_DIR / "web_traffic.csv"

# Load data
traffic_df = pd.read_csv(TRAFFIC_CSV)

# Create MCP server
server = Server("web-traffic-data")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available web traffic tools."""
    return [
        Tool(
            name="get_traffic_metrics",
            description="Get current web traffic metrics including sessions, users, and engagement",
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
            name="get_traffic_trend",
            description="Get traffic trend analysis (QoQ growth/decline)",
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
            name="get_engagement_quality",
            description="Analyze engagement quality (bounce rate, session duration, conversion)",
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
            name="assess_digital_health",
            description="Overall digital health assessment combining traffic and engagement",
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
    
    if name == "get_traffic_metrics":
        traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
        
        if traffic_row.empty:
            return [TextContent(
                type="text",
                text=f"No traffic data found for SME {sme_id}"
            )]
        
        data = traffic_row.iloc[0]
        
        metrics = {
            "sme_id": sme_id,
            "monthly_sessions": int(data['sessions_monthly']),
            "monthly_users": int(data['users_monthly']),
            "avg_session_duration_sec": int(data['avg_session_duration_sec']),
            "bounce_rate": round(float(data['bounce_rate']), 3),
            "conversion_rate_pct": float(data['conversion_rate']),
            "top_traffic_source": data['top_source'],
            "last_updated": data['last_updated']
        }
        
        return [TextContent(
            type="text",
            text=f"Web Traffic Metrics:\n{pd.Series(metrics).to_string()}"
        )]
    
    elif name == "get_traffic_trend":
        traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
        
        if traffic_row.empty:
            return [TextContent(
                type="text",
                text=f"No trend data found for SME {sme_id}"
            )]
        
        data = traffic_row.iloc[0]
        
        sessions_change = float(data['sessions_change_qoq'])
        users_change = float(data['users_change_qoq'])
        
        trend = {
            "sme_id": sme_id,
            "sessions_change_qoq_pct": sessions_change,
            "users_change_qoq_pct": users_change,
            "trend_direction": _determine_trend(sessions_change),
            "risk_level": _assess_traffic_risk(sessions_change),
            "interpretation": _interpret_traffic_trend(sessions_change, users_change)
        }
        
        return [TextContent(
            type="text",
            text=f"Traffic Trend Analysis:\n{pd.Series(trend).to_string()}"
        )]
    
    elif name == "get_engagement_quality":
        traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
        
        if traffic_row.empty:
            return [TextContent(
                type="text",
                text=f"No engagement data found for SME {sme_id}"
            )]
        
        data = traffic_row.iloc[0]
        
        bounce_rate = float(data['bounce_rate'])
        avg_duration = int(data['avg_session_duration_sec'])
        conversion_rate = float(data['conversion_rate'])
        
        quality_score = _calculate_engagement_score(bounce_rate, avg_duration, conversion_rate)
        
        engagement = {
            "sme_id": sme_id,
            "bounce_rate": round(bounce_rate, 3),
            "avg_session_duration_min": round(avg_duration / 60, 1),
            "conversion_rate_pct": conversion_rate,
            "engagement_quality_score": quality_score,
            "quality_rating": _rate_engagement(quality_score),
            "interpretation": _interpret_engagement(bounce_rate, avg_duration, conversion_rate)
        }
        
        return [TextContent(
            type="text",
            text=f"Engagement Quality:\n{pd.Series(engagement).to_string()}"
        )]
    
    elif name == "assess_digital_health":
        traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
        
        if traffic_row.empty:
            return [TextContent(
                type="text",
                text=f"No data found for SME {sme_id}"
            )]
        
        data = traffic_row.iloc[0]
        
        # Calculate composite digital health score
        sessions_change = float(data['sessions_change_qoq'])
        bounce_rate = float(data['bounce_rate'])
        avg_duration = int(data['avg_session_duration_sec'])
        conversion_rate = float(data['conversion_rate'])
        
        # Traffic trend score (0-100, lower is better for risk)
        traffic_score = _score_traffic_trend(sessions_change)
        
        # Engagement score (0-100, lower is better for risk)
        engagement_score = _score_engagement(bounce_rate, avg_duration, conversion_rate)
        
        # Overall digital health (weighted average)
        health_score = (traffic_score * 0.6) + (engagement_score * 0.4)
        
        assessment = {
            "sme_id": sme_id,
            "overall_health_score": round(health_score, 1),
            "health_rating": _rate_digital_health(health_score),
            "traffic_component": round(traffic_score, 1),
            "engagement_component": round(engagement_score, 1),
            "key_concerns": _identify_concerns(sessions_change, bounce_rate, avg_duration),
            "risk_to_credit": _map_to_credit_risk(health_score)
        }
        
        return [TextContent(
            type="text",
            text=f"Digital Health Assessment:\n{pd.Series({k: v for k, v in assessment.items() if k != 'key_concerns'}).to_string()}\n\nKey Concerns:\n{', '.join(assessment['key_concerns']) if assessment['key_concerns'] else 'None'}"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

def _determine_trend(change_pct: float) -> str:
    """Determine trend direction."""
    if change_pct > 5:
        return "Growing"
    elif change_pct < -5:
        return "Declining"
    else:
        return "Stable"

def _assess_traffic_risk(change_pct: float) -> str:
    """Assess risk level from traffic trend."""
    if change_pct < -40:
        return "CRITICAL"
    elif change_pct < -25:
        return "HIGH"
    elif change_pct < -10:
        return "MEDIUM"
    elif change_pct < -5:
        return "LOW"
    else:
        return "MINIMAL"

def _interpret_traffic_trend(sessions_change: float, users_change: float) -> str:
    """Interpret traffic trend for credit risk."""
    if sessions_change < -40:
        return "🔴 CRITICAL: Massive traffic collapse - demand crisis likely"
    elif sessions_change < -25:
        return "🟠 HIGH RISK: Significant traffic decline - losing market position"
    elif sessions_change < -15:
        return "🟡 MEDIUM RISK: Notable traffic decline - customer interest waning"
    elif sessions_change < -5:
        return "⚠️ LOW RISK: Slight traffic decline - monitor closely"
    elif sessions_change < 10:
        return "✅ STABLE: Traffic stable - normal market position"
    else:
        return "🟢 POSITIVE: Traffic growing - increasing demand/interest"

def _calculate_engagement_score(bounce_rate: float, duration: int, conversion: float) -> float:
    """Calculate engagement quality score (0-100)."""
    # Lower bounce rate is better
    bounce_component = max(0, 100 - (bounce_rate * 150))
    
    # Higher duration is better (target ~180 seconds)
    duration_component = min(100, (duration / 180) * 100)
    
    # Higher conversion is better (scale to typical 2-5% range)
    conversion_component = min(100, (conversion / 5) * 100)
    
    # Weighted average
    score = (bounce_component * 0.4) + (duration_component * 0.3) + (conversion_component * 0.3)
    return round(score, 1)

def _rate_engagement(score: float) -> str:
    """Rate engagement quality."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    elif score >= 20:
        return "Poor"
    else:
        return "Very Poor"

def _interpret_engagement(bounce_rate: float, duration: int, conversion: float) -> str:
    """Interpret engagement quality."""
    if bounce_rate > 0.70 and duration < 120:
        return "🔴 CRITICAL: Very high bounce rate + low engagement = poor product-market fit"
    elif bounce_rate > 0.60 and conversion < 2.0:
        return "🟠 WARNING: High bounce, low conversion = value proposition issues"
    elif bounce_rate > 0.50:
        return "🟡 CAUTION: Elevated bounce rate - UX or targeting problems"
    elif conversion < 2.0:
        return "⚠️ WATCH: Low conversion despite decent traffic - funnel issues"
    elif bounce_rate < 0.40 and duration > 180 and conversion > 3.5:
        return "🟢 EXCELLENT: High engagement + good conversion = strong business"
    else:
        return "✅ NORMAL: Acceptable engagement metrics"

def _score_traffic_trend(change_pct: float) -> float:
    """Score traffic trend (0=excellent, 100=critical risk)."""
    if change_pct >= 20:
        return 5  # Excellent growth
    elif change_pct >= 10:
        return 15  # Good growth
    elif change_pct >= 0:
        return 30  # Stable
    elif change_pct >= -10:
        return 50  # Slight decline
    elif change_pct >= -25:
        return 70  # Concerning decline
    elif change_pct >= -40:
        return 85  # Severe decline
    else:
        return 95  # Critical collapse

def _score_engagement(bounce_rate: float, duration: int, conversion: float) -> float:
    """Score engagement (0=excellent, 100=critical risk)."""
    # Bounce rate component
    if bounce_rate < 0.35:
        bounce_score = 10
    elif bounce_rate < 0.45:
        bounce_score = 25
    elif bounce_rate < 0.55:
        bounce_score = 45
    elif bounce_rate < 0.65:
        bounce_score = 65
    else:
        bounce_score = 85
    
    # Duration component
    if duration > 240:
        duration_score = 10
    elif duration > 180:
        duration_score = 25
    elif duration > 120:
        duration_score = 45
    elif duration > 90:
        duration_score = 65
    else:
        duration_score = 85
    
    # Conversion component
    if conversion > 4.5:
        conversion_score = 10
    elif conversion > 3.5:
        conversion_score = 25
    elif conversion > 2.5:
        conversion_score = 45
    elif conversion > 1.5:
        conversion_score = 65
    else:
        conversion_score = 85
    
    # Weighted average
    return (bounce_score * 0.4) + (duration_score * 0.3) + (conversion_score * 0.3)

def _rate_digital_health(score: float) -> str:
    """Rate overall digital health."""
    if score < 25:
        return "Excellent (Low Risk)"
    elif score < 40:
        return "Good (Low-Medium Risk)"
    elif score < 60:
        return "Fair (Medium Risk)"
    elif score < 75:
        return "Poor (High Risk)"
    else:
        return "Critical (Very High Risk)"

def _identify_concerns(sessions_change: float, bounce_rate: float, duration: int) -> list[str]:
    """Identify key concerns."""
    concerns = []
    
    if sessions_change < -30:
        concerns.append("Severe traffic decline")
    elif sessions_change < -15:
        concerns.append("Significant traffic decline")
    
    if bounce_rate > 0.65:
        concerns.append("Very high bounce rate")
    elif bounce_rate > 0.55:
        concerns.append("Elevated bounce rate")
    
    if duration < 120:
        concerns.append("Low engagement time")
    
    return concerns

def _map_to_credit_risk(health_score: float) -> str:
    """Map digital health to credit risk points."""
    if health_score < 30:
        return "Adds 10-15 points to risk score"
    elif health_score < 50:
        return "Adds 20-30 points to risk score"
    elif health_score < 70:
        return "Adds 40-55 points to risk score"
    else:
        return "Adds 65-85 points to risk score (critical factor)"

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