#!/usr/bin/env python3
"""
News Intelligence MCP Server - Cloud Run Compatible
Provides news events, sentiment analysis, and risk signals.
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from fastmcp import FastMCP

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
NEWS_CSV = DATA_DIR / "news_events.csv"

# Load data
news_df = pd.read_csv(NEWS_CSV)
news_df['event_date'] = pd.to_datetime(news_df['event_date'])

# Create FastMCP server
mcp = FastMCP("news-intelligence")


@mcp.tool()
def get_recent_events(sme_id: str, days: int = 90) -> dict:
    """Get recent news events for an SME"""
    # Filter events for this SME within time window
    cutoff = datetime.now() - timedelta(days=days)
    events = news_df[
        (news_df['sme_id'] == sme_id) & 
        (news_df['event_date'] >= cutoff)
    ].sort_values('event_date', ascending=False)
    
    if events.empty:
        return {"info": f"No news events found for SME {sme_id} in last {days} days"}
    
    # Format events
    events_list = []
    for idx, row in events.iterrows():
        events_list.append({
            "date": row['event_date'].strftime('%Y-%m-%d'),
            "type": row['event_type'],
            "severity": row['severity'],
            "title": row['title'],
            "summary": row['summary'],
            "source": row['source'],
            "sentiment_score": round(float(row['sentiment_score']), 2),
            "impact_score": int(row['impact_score']),
            "verified": bool(row['verified'])
        })
    
    summary = {
        "sme_id": sme_id,
        "total_events": len(events),
        "critical_events": len(events[events['severity'] == 'critical']),
        "warning_events": len(events[events['severity'] == 'warning']),
        "info_events": len(events[events['severity'] == 'info']),
        "avg_sentiment": round(events['sentiment_score'].mean(), 2),
        "avg_impact": round(events['impact_score'].mean(), 1),
        "events": events_list
    }
    
    return summary


@mcp.tool()
def get_critical_events(sme_id: str, days: int = 90) -> dict:
    """Get critical/high-severity events only"""
    # Filter critical/warning events only
    cutoff = datetime.now() - timedelta(days=days)
    critical_events = news_df[
        (news_df['sme_id'] == sme_id) & 
        (news_df['event_date'] >= cutoff) &
        (news_df['severity'].isin(['critical', 'warning']))
    ].sort_values('event_date', ascending=False)
    
    if critical_events.empty:
        return {"info": f"✅ No critical events for SME {sme_id} in last {days} days"}
    
    # Format critical events
    events_list = []
    for idx, row in critical_events.iterrows():
        events_list.append({
            "date": row['event_date'].strftime('%Y-%m-%d'),
            "severity": row['severity'],
            "type": row['event_type'],
            "title": row['title'],
            "summary": row['summary'],
            "impact_score": int(row['impact_score'])
        })
    
    return {
        "alert": f"🔴 Critical Events Found: {len(critical_events)}",
        "events": events_list
    }


@mcp.tool()
def get_sentiment_analysis(sme_id: str, days: int = 90) -> dict:
    """Get overall news sentiment and trend for an SME"""
    # Analyze sentiment over time
    cutoff = datetime.now() - timedelta(days=days)
    events = news_df[
        (news_df['sme_id'] == sme_id) & 
        (news_df['event_date'] >= cutoff)
    ]
    
    if events.empty:
        return {"info": f"No events to analyze for SME {sme_id}"}
    
    # Calculate sentiment metrics
    avg_sentiment = events['sentiment_score'].mean()
    sentiment_trend = _calculate_sentiment_trend(events)
    
    # Categorize events by sentiment
    very_negative = len(events[events['sentiment_score'] < -0.6])
    negative = len(events[(events['sentiment_score'] >= -0.6) & (events['sentiment_score'] < -0.2)])
    neutral = len(events[(events['sentiment_score'] >= -0.2) & (events['sentiment_score'] <= 0.2)])
    positive = len(events[(events['sentiment_score'] > 0.2) & (events['sentiment_score'] <= 0.6)])
    very_positive = len(events[events['sentiment_score'] > 0.6])
    
    analysis = {
        "sme_id": sme_id,
        "analysis_period_days": days,
        "total_events": len(events),
        "avg_sentiment_score": round(avg_sentiment, 2),
        "sentiment_rating": _rate_sentiment(avg_sentiment),
        "sentiment_trend": sentiment_trend,
        "very_negative_events": very_negative,
        "negative_events": negative,
        "neutral_events": neutral,
        "positive_events": positive,
        "very_positive_events": very_positive
    }
    
    return analysis


@mcp.tool()
def assess_news_risk(sme_id: str) -> dict:
    """Overall news-based risk assessment"""
    # Comprehensive news risk assessment
    cutoff_30 = datetime.now() - timedelta(days=30)
    cutoff_90 = datetime.now() - timedelta(days=90)
    
    events_30 = news_df[
        (news_df['sme_id'] == sme_id) & 
        (news_df['event_date'] >= cutoff_30)
    ]
    
    events_90 = news_df[
        (news_df['sme_id'] == sme_id) & 
        (news_df['event_date'] >= cutoff_90)
    ]
    
    if events_90.empty:
        return {"info": f"✅ No news events found for SME {sme_id} - insufficient data for risk assessment"}
    
    # Calculate risk score from news
    risk_score = _calculate_news_risk_score(events_30, events_90)
    
    # Identify key risk factors
    risk_factors = _identify_news_risk_factors(events_30, events_90)
    
    assessment = {
        "sme_id": sme_id,
        "news_risk_score": round(risk_score, 1),
        "risk_rating": _rate_news_risk(risk_score),
        "events_30d": len(events_30),
        "events_90d": len(events_90),
        "critical_events_30d": len(events_30[events_30['severity'] == 'critical']),
        "avg_sentiment_30d": round(events_30['sentiment_score'].mean(), 2) if len(events_30) > 0 else 0,
        "avg_impact_30d": round(events_30['impact_score'].mean(), 1) if len(events_30) > 0 else 0,
        "key_risk_factors": risk_factors,
        "risk_contribution": f"Adds {_news_risk_points(risk_score)} points to overall risk score"
    }
    
    return assessment


# Helper functions
def _calculate_sentiment_trend(events: pd.DataFrame) -> str:
    """Calculate sentiment trend over time."""
    if len(events) < 3:
        return "Insufficient data"
    
    # Split into first half and second half
    mid_point = len(events) // 2
    sorted_events = events.sort_values('event_date')
    
    first_half = sorted_events.iloc[:mid_point]['sentiment_score'].mean()
    second_half = sorted_events.iloc[mid_point:]['sentiment_score'].mean()
    
    diff = second_half - first_half
    
    if diff > 0.2:
        return "📈 Improving (Sentiment getting more positive)"
    elif diff < -0.2:
        return "📉 Deteriorating (Sentiment getting more negative)"
    else:
        return "➡️ Stable (No significant trend)"


def _rate_sentiment(score: float) -> str:
    """Rate overall sentiment."""
    if score > 0.6:
        return "Very Positive"
    elif score > 0.2:
        return "Positive"
    elif score >= -0.2:
        return "Neutral"
    elif score >= -0.6:
        return "Negative"
    else:
        return "Very Negative"


def _calculate_news_risk_score(events_30: pd.DataFrame, events_90: pd.DataFrame) -> float:
    """Calculate news-based risk score (0-100, higher = worse)."""
    score = 20  # Base score
    
    # Critical events in last 30 days
    critical_30 = len(events_30[events_30['severity'] == 'critical'])
    score += critical_30 * 15
    
    # Warning events in last 30 days
    warning_30 = len(events_30[events_30['severity'] == 'warning'])
    score += warning_30 * 8
    
    # Average sentiment (last 30 days)
    if len(events_30) > 0:
        avg_sentiment = events_30['sentiment_score'].mean()
        if avg_sentiment < -0.6:
            score += 25
        elif avg_sentiment < -0.3:
            score += 15
        elif avg_sentiment < 0:
            score += 5
    
    # High impact events
    high_impact = len(events_30[events_30['impact_score'] >= 10])
    score += high_impact * 10
    
    # Event frequency (many events can indicate instability)
    if len(events_30) >= 5:
        score += 10
    
    # Specific event types (high risk)
    litigation = len(events_30[events_30['event_type'].isin(['litigation', 'compliance'])])
    score += litigation * 20
    
    departures = len(events_30[events_30['event_type'] == 'departure'])
    score += departures * 10
    
    return min(score, 100)


def _rate_news_risk(score: float) -> str:
    """Rate news-based risk."""
    if score < 25:
        return "Low (Positive/Neutral coverage)"
    elif score < 40:
        return "Low-Medium (Some concerns)"
    elif score < 60:
        return "Medium (Notable negative coverage)"
    elif score < 75:
        return "High (Significant negative events)"
    else:
        return "Critical (Multiple severe events)"


def _identify_news_risk_factors(events_30: pd.DataFrame, events_90: pd.DataFrame) -> list:
    """Identify key news risk factors."""
    factors = []
    
    critical_30 = len(events_30[events_30['severity'] == 'critical'])
    if critical_30 >= 3:
        factors.append(f"Multiple critical events in last 30 days ({critical_30})")
    elif critical_30 >= 1:
        factors.append(f"Critical event in last 30 days")
    
    litigation = len(events_30[events_30['event_type'].isin(['litigation', 'compliance'])])
    if litigation > 0:
        factors.append(f"Legal/compliance issues ({litigation} events)")
    
    departures = len(events_30[events_30['event_type'] == 'departure'])
    if departures >= 2:
        factors.append(f"Multiple departures reported ({departures})")
    
    if len(events_30) > 0:
        avg_sentiment = events_30['sentiment_score'].mean()
        if avg_sentiment < -0.5:
            factors.append("Predominantly negative media coverage")
    
    customer_issues = len(events_30[events_30['event_type'].isin(['customer_loss', 'reputation'])])
    if customer_issues > 0:
        factors.append(f"Customer/reputation concerns ({customer_issues} events)")
    
    return factors


def _news_risk_points(score: float) -> str:
    """Map news risk to risk score points."""
    if score < 30:
        return "5-15"
    elif score < 50:
        return "15-30"
    elif score < 70:
        return "30-50"
    else:
        return "50-95"


if __name__ == "__main__":
    # Use streamable-http for Cloud Run deployment
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8004))
    )