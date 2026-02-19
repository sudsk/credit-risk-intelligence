#!/usr/bin/env python3
"""
Web Traffic MCP Server - Cloud Run Compatible
Provides website traffic, engagement metrics, and digital presence analysis.
"""
import os
import pandas as pd
from pathlib import Path
from fastmcp import FastMCP

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
WEB_TRAFFIC_CSV = DATA_DIR / "web_traffic.csv"

# Load data
traffic_df = pd.read_csv(WEB_TRAFFIC_CSV)

# Create FastMCP server
mcp = FastMCP("web-traffic-data")


@mcp.tool()
def get_traffic_metrics(sme_id: str) -> dict:
    """Get website traffic metrics and trends"""
    traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
    
    if traffic_row.empty:
        return {"error": f"No traffic data found for SME {sme_id}"}
    
    data = traffic_row.iloc[0]
    
    metrics = {
        "sme_id": sme_id,
        "monthly_visitors": int(data['monthly_visitors']),
        "traffic_change_30d": f"{float(data['traffic_change_30d']):.1f}%",
        "traffic_change_90d": f"{float(data['traffic_change_90d']):.1f}%",
        "bounce_rate": f"{float(data['bounce_rate']) * 100:.1f}%",
        "avg_session_duration_seconds": int(data['avg_session_duration_seconds']),
        "pages_per_session": round(float(data['pages_per_session']), 2),
        "conversion_rate": f"{float(data['conversion_rate']) * 100:.2f}%"
    }
    
    return metrics


@mcp.tool()
def get_traffic_trend(sme_id: str) -> dict:
    """Analyze traffic trends over 30 and 90 days"""
    traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
    
    if traffic_row.empty:
        return {"error": f"No trend data found for SME {sme_id}"}
    
    data = traffic_row.iloc[0]
    
    current_visitors = int(data['monthly_visitors'])
    change_30d = float(data['traffic_change_30d'])
    change_90d = float(data['traffic_change_90d'])
    
    # Calculate historical visitor counts
    visitors_30d_ago = int(current_visitors / (1 + change_30d/100))
    visitors_90d_ago = int(current_visitors / (1 + change_90d/100))
    
    trend = {
        "sme_id": sme_id,
        "current_monthly_visitors": current_visitors,
        "visitors_30_days_ago": visitors_30d_ago,
        "visitors_90_days_ago": visitors_90d_ago,
        "change_30d": f"{change_30d:.1f}%",
        "change_90d": f"{change_90d:.1f}%",
        "trend_direction": _assess_traffic_trend(change_30d, change_90d),
        "traffic_health": _rate_traffic_health(current_visitors, change_30d)
    }
    
    return trend


@mcp.tool()
def get_engagement_metrics(sme_id: str) -> dict:
    """Get user engagement metrics (bounce rate, session duration, pages per session)"""
    traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
    
    if traffic_row.empty:
        return {"error": f"No engagement data found for SME {sme_id}"}
    
    data = traffic_row.iloc[0]
    
    bounce_rate = float(data['bounce_rate']) * 100
    session_duration = int(data['avg_session_duration_seconds'])
    pages_per_session = float(data['pages_per_session'])
    
    engagement = {
        "sme_id": sme_id,
        "bounce_rate": f"{bounce_rate:.1f}%",
        "avg_session_duration": f"{session_duration // 60}m {session_duration % 60}s",
        "pages_per_session": round(pages_per_session, 2),
        "engagement_rating": _rate_engagement(bounce_rate, session_duration, pages_per_session),
        "engagement_health": _assess_engagement_health(bounce_rate, session_duration, pages_per_session)
    }
    
    return engagement


@mcp.tool()
def get_conversion_analysis(sme_id: str) -> dict:
    """Analyze conversion rate and effectiveness"""
    traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
    
    if traffic_row.empty:
        return {"error": f"No conversion data found for SME {sme_id}"}
    
    data = traffic_row.iloc[0]
    
    conversion_rate = float(data['conversion_rate']) * 100
    monthly_visitors = int(data['monthly_visitors'])
    estimated_conversions = int(monthly_visitors * float(data['conversion_rate']))
    
    analysis = {
        "sme_id": sme_id,
        "conversion_rate": f"{conversion_rate:.2f}%",
        "monthly_visitors": monthly_visitors,
        "estimated_monthly_conversions": estimated_conversions,
        "conversion_rating": _rate_conversion(conversion_rate),
        "conversion_health": _assess_conversion_health(conversion_rate)
    }
    
    return analysis


@mcp.tool()
def assess_digital_presence(sme_id: str) -> dict:
    """Overall digital presence and web health assessment"""
    traffic_row = traffic_df[traffic_df['sme_id'] == sme_id]
    
    if traffic_row.empty:
        return {"error": f"No digital presence data found for SME {sme_id}"}
    
    data = traffic_row.iloc[0]
    
    # Calculate digital presence score
    presence_score = _calculate_digital_presence_score(data)
    
    # Identify concerns
    concerns = _identify_digital_concerns(data)
    
    assessment = {
        "sme_id": sme_id,
        "digital_presence_score": round(presence_score, 1),
        "presence_rating": _rate_digital_presence(presence_score),
        "monthly_visitors": int(data['monthly_visitors']),
        "traffic_change_30d": f"{float(data['traffic_change_30d']):.1f}%",
        "bounce_rate": f"{float(data['bounce_rate']) * 100:.1f}%",
        "conversion_rate": f"{float(data['conversion_rate']) * 100:.2f}%",
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_digital_risk_points(presence_score)} points to overall risk score"
    }
    
    return assessment


# Helper functions
def _assess_traffic_trend(change_30d: float, change_90d: float) -> str:
    """Assess traffic trend direction."""
    if change_90d < -30:
        return "🔴 CRITICAL: Severe traffic decline (>-30% in 90d)"
    elif change_90d < -15:
        return "🟠 WARNING: Significant traffic decline (-15 to -30% in 90d)"
    elif change_30d < -10:
        return "🟡 CONCERN: Recent traffic drop (>-10% in 30d)"
    elif change_90d < 0:
        return "⚠️ WATCH: Gradual traffic decline"
    elif change_30d > 20:
        return "🟢 EXCELLENT: Strong growth (>20% in 30d)"
    elif change_90d > 10:
        return "✅ POSITIVE: Growing traffic"
    else:
        return "➡️ STABLE: Flat traffic"


def _rate_traffic_health(visitors: int, change_30d: float) -> str:
    """Rate traffic health."""
    if visitors >= 100000 and change_30d >= 10:
        return "Excellent (High volume + growth)"
    elif visitors >= 50000 and change_30d >= 0:
        return "Good (Strong volume + stable/growing)"
    elif visitors >= 10000:
        return "Adequate (Moderate volume)"
    elif visitors >= 1000:
        return "Weak (Low volume)"
    else:
        return "Poor (Very low volume)"


def _rate_engagement(bounce_rate: float, session_duration: int, pages_per_session: float) -> str:
    """Rate engagement quality."""
    if bounce_rate < 30 and session_duration >= 180 and pages_per_session >= 4:
        return "Excellent (Highly engaged users)"
    elif bounce_rate < 40 and session_duration >= 120 and pages_per_session >= 3:
        return "Good (Strong engagement)"
    elif bounce_rate < 55 and session_duration >= 60 and pages_per_session >= 2:
        return "Adequate (Moderate engagement)"
    elif bounce_rate < 70:
        return "Weak (Low engagement)"
    else:
        return "Poor (Very low engagement)"


def _assess_engagement_health(bounce_rate: float, session_duration: int, pages_per_session: float) -> str:
    """Assess engagement health."""
    if bounce_rate > 75:
        return "🔴 CRITICAL: Very high bounce rate indicates poor UX or content"
    elif session_duration < 30:
        return "🟠 WARNING: Very short sessions suggest low interest"
    elif bounce_rate > 60:
        return "🟡 CONCERN: High bounce rate"
    elif pages_per_session < 1.5:
        return "⚠️ WATCH: Limited page exploration"
    else:
        return "✅ HEALTHY: Good user engagement"


def _rate_conversion(conversion_rate: float) -> str:
    """Rate conversion effectiveness."""
    if conversion_rate >= 10:
        return "Excellent (>10%)"
    elif conversion_rate >= 5:
        return "Good (5-10%)"
    elif conversion_rate >= 2:
        return "Adequate (2-5%)"
    elif conversion_rate >= 1:
        return "Weak (1-2%)"
    else:
        return "Poor (<1%)"


def _assess_conversion_health(conversion_rate: float) -> str:
    """Assess conversion health."""
    if conversion_rate < 0.5:
        return "🔴 CRITICAL: Very low conversion indicates major funnel issues"
    elif conversion_rate < 1:
        return "🟠 WARNING: Low conversion rate needs optimization"
    elif conversion_rate < 2:
        return "🟡 FAIR: Below average conversion"
    else:
        return "✅ HEALTHY: Good conversion performance"


def _calculate_digital_presence_score(data: pd.Series) -> float:
    """Calculate digital presence score (0-100, higher = worse)."""
    score = 15  # Base score
    
    # Traffic volume
    visitors = int(data['monthly_visitors'])
    if visitors < 1000:
        score += 40
    elif visitors < 5000:
        score += 25
    elif visitors < 20000:
        score += 10
    
    # Traffic trend
    change_30d = float(data['traffic_change_30d'])
    change_90d = float(data['traffic_change_90d'])
    
    if change_90d < -30:
        score += 35
    elif change_90d < -15:
        score += 25
    elif change_30d < -10:
        score += 15
    elif change_90d < -5:
        score += 8
    
    # Engagement
    bounce_rate = float(data['bounce_rate']) * 100
    session_duration = int(data['avg_session_duration_seconds'])
    
    if bounce_rate > 75:
        score += 25
    elif bounce_rate > 60:
        score += 15
    elif bounce_rate > 50:
        score += 8
    
    if session_duration < 30:
        score += 20
    elif session_duration < 60:
        score += 10
    
    # Conversion
    conversion_rate = float(data['conversion_rate']) * 100
    if conversion_rate < 0.5:
        score += 25
    elif conversion_rate < 1:
        score += 15
    elif conversion_rate < 2:
        score += 8
    
    return min(score, 100)


def _rate_digital_presence(score: float) -> str:
    """Rate digital presence."""
    if score < 25:
        return "Excellent (Strong online presence)"
    elif score < 40:
        return "Good (Solid online presence)"
    elif score < 60:
        return "Fair (Moderate online presence)"
    elif score < 75:
        return "Poor (Weak online presence)"
    else:
        return "Critical (Very weak online presence)"


def _identify_digital_concerns(data: pd.Series) -> list:
    """Identify digital presence concerns."""
    concerns = []
    
    # Traffic
    visitors = int(data['monthly_visitors'])
    change_30d = float(data['traffic_change_30d'])
    change_90d = float(data['traffic_change_90d'])
    
    if visitors < 1000:
        concerns.append(f"Very low traffic volume ({visitors:,} monthly visitors)")
    elif visitors < 5000:
        concerns.append(f"Low traffic volume ({visitors:,} monthly visitors)")
    
    if change_90d < -20:
        concerns.append(f"Severe traffic decline ({change_90d:.1f}% in 90 days)")
    elif change_90d < -10:
        concerns.append(f"Significant traffic decline ({change_90d:.1f}% in 90 days)")
    
    # Engagement
    bounce_rate = float(data['bounce_rate']) * 100
    session_duration = int(data['avg_session_duration_seconds'])
    
    if bounce_rate > 70:
        concerns.append(f"Very high bounce rate ({bounce_rate:.1f}%)")
    elif bounce_rate > 60:
        concerns.append(f"High bounce rate ({bounce_rate:.1f}%)")
    
    if session_duration < 30:
        concerns.append(f"Very short session duration ({session_duration}s)")
    elif session_duration < 60:
        concerns.append(f"Short session duration ({session_duration}s)")
    
    # Conversion
    conversion_rate = float(data['conversion_rate']) * 100
    if conversion_rate < 0.5:
        concerns.append(f"Very low conversion rate ({conversion_rate:.2f}%)")
    elif conversion_rate < 1:
        concerns.append(f"Low conversion rate ({conversion_rate:.2f}%)")
    
    return concerns


def _digital_risk_points(presence_score: float) -> str:
    """Map digital presence to risk points."""
    if presence_score < 30:
        return "5-10"
    elif presence_score < 50:
        return "10-20"
    elif presence_score < 70:
        return "20-35"
    else:
        return "35-55"


if __name__ == "__main__":
    # Use streamable-http for Cloud Run deployment
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8006))
    )