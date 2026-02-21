#!/usr/bin/env python3
"""
Unified Data MCP Server - Cloud Run Compatible
Replaces all 6 individual MCP servers (companies_house, financial, linkedin,
news, payment_data, web_traffic) with a single server on port 8001.

All CSVs are loaded once at startup. Agents call this server for all data needs.
"""
import os
import statistics
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Data paths & loading
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent / "data"

# Load all CSVs once at startup
companies_df  = pd.read_csv(DATA_DIR / "company_info.csv")
financial_df  = pd.read_csv(DATA_DIR / "financial_data.csv")
employees_df  = pd.read_csv(DATA_DIR / "employees.csv")
departures_df = pd.read_csv(DATA_DIR / "departures.csv")
news_df       = pd.read_csv(DATA_DIR / "news_events.csv")
traffic_df    = pd.read_csv(DATA_DIR / "web_traffic.csv")
smes_df       = pd.read_csv(DATA_DIR / "smes.csv")

# Parse date columns once
news_df['event_date']      = pd.to_datetime(news_df['event_date'])
departures_df['left_date'] = pd.to_datetime(departures_df['left_date'])

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("credit-data")


# ===========================================================================
# COMPANIES HOUSE TOOLS
# (from companies_house_server.py — port 8001)
# ===========================================================================

@mcp.tool()
def get_company_info(sme_id: str) -> dict:
    """Get official company registration details and status"""
    row = companies_df[companies_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No company data found for SME {sme_id}"}
    data = row.iloc[0]
    return {
        "sme_id": sme_id,
        "company_number": data['company_number'],
        "company_status": data['company_status'],
        "incorporation_date": data['incorporation_date'],
        "registered_address_postcode": data['registered_address_postcode'],
        "sic_code": data['sic_code'],
        "director_count": int(data['director_count']),
        "last_accounts_date": data['last_accounts_date'],
        "next_accounts_due": data['next_accounts_due'],
        "last_updated": data['last_updated'],
    }


@mcp.tool()
def check_compliance_status(sme_id: str) -> dict:
    """Check regulatory compliance, overdue accounts, and CCJs"""
    row = companies_df[companies_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No compliance data found for SME {sme_id}"}
    data = row.iloc[0]

    next_due     = pd.to_datetime(data['next_accounts_due'])
    is_overdue   = next_due < datetime.now()
    days_overdue = (datetime.now() - next_due).days if is_overdue else 0
    ccj_count    = int(data['ccj_count'])
    insolvency   = bool(data['insolvency_flag'])

    return {
        "sme_id": sme_id,
        "accounts_overdue": is_overdue,
        "days_overdue": days_overdue,
        "next_accounts_due": data['next_accounts_due'],
        "ccj_count": ccj_count,
        "insolvency_flag": insolvency,
        "compliance_status": _assess_compliance(is_overdue, days_overdue, ccj_count, insolvency),
        "risk_level": _compliance_risk_level(is_overdue, days_overdue, ccj_count, insolvency),
    }


@mcp.tool()
def get_director_changes(sme_id: str) -> dict:
    """Get director change history over the past 12 months"""
    row = companies_df[companies_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No director data found for SME {sme_id}"}
    data = row.iloc[0]

    changes = int(data['director_changes_12m'])
    current = int(data['director_count'])

    return {
        "sme_id": sme_id,
        "director_count": current,
        "director_changes_12m": changes,
        "director_stability": _assess_director_stability(changes, current),
    }


@mcp.tool()
def assess_corporate_health(sme_id: str) -> dict:
    """Overall corporate health assessment from regulatory perspective"""
    row = companies_df[companies_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No corporate data found for SME {sme_id}"}
    data = row.iloc[0]

    next_due     = pd.to_datetime(data['next_accounts_due'])
    is_overdue   = next_due < datetime.now()
    days_overdue = (datetime.now() - next_due).days if is_overdue else 0
    insolvency   = bool(data['insolvency_flag'])
    ccj_count    = int(data['ccj_count'])
    dir_changes  = int(data['director_changes_12m'])
    status       = data['company_status']

    health_score = _calculate_corporate_health_score(
        is_overdue, days_overdue, ccj_count, insolvency, dir_changes, status
    )
    key_concerns = _identify_corporate_concerns(
        is_overdue, days_overdue, ccj_count, insolvency, dir_changes
    )

    return {
        "sme_id": sme_id,
        "corporate_health_score": round(health_score, 1),
        "health_rating": _rate_corporate_health(health_score),
        "company_status": status,
        "key_concerns": key_concerns,
        "risk_contribution": f"Adds {_corporate_risk_points(health_score)} points to overall risk score",
    }


# ===========================================================================
# FINANCIAL TOOLS
# (from financial_server.py — port 8002)
# ===========================================================================

@mcp.tool()
def get_financial_metrics(sme_id: str) -> dict:
    """Get current quarter financial metrics and ratios"""
    row = financial_df[financial_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No financial data found for SME {sme_id}"}
    data = row.iloc[0]
    return {
        "sme_id": sme_id,
        "revenue_q4": f"€{int(data['revenue_q4']):,}",
        "ebitda_margin": f"{float(data['ebitda_margin']) * 100:.1f}%",
        "gross_margin": f"{float(data['gross_margin']) * 100:.1f}%",
        "net_margin": f"{float(data['net_margin']) * 100:.1f}%",
        "revenue_growth_yoy": f"{float(data['revenue_growth_yoy']):.1f}%",
        "revenue_growth_qoq": f"{float(data['revenue_growth_qoq']):.1f}%",
        "current_ratio": round(float(data['current_ratio']), 2),
        "debt_to_equity": round(float(data['debt_to_equity']), 2),
        "interest_coverage": round(float(data['interest_coverage']), 2),
        "roa": f"{float(data['roa']) * 100:.1f}%",
        "roe": f"{float(data['roe']) * 100:.1f}%",
    }


@mcp.tool()
def get_revenue_trend(sme_id: str) -> dict:
    """Get quarterly revenue trend analysis"""
    row = financial_df[financial_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No revenue data found for SME {sme_id}"}
    data = row.iloc[0]

    q1, q2, q3, q4 = (int(data[f'revenue_q{i}']) for i in range(1, 5))

    return {
        "sme_id": sme_id,
        "revenue_q1": f"€{q1:,}",
        "revenue_q2": f"€{q2:,}",
        "revenue_q3": f"€{q3:,}",
        "revenue_q4": f"€{q4:,}",
        "revenue_growth_yoy": f"{float(data['revenue_growth_yoy']):.1f}%",
        "revenue_growth_qoq": f"{float(data['revenue_growth_qoq']):.1f}%",
        "trend_direction": _assess_revenue_trend(q1, q2, q3, q4),
        "volatility": _assess_revenue_volatility([q1, q2, q3, q4]),
    }


@mcp.tool()
def get_liquidity_analysis(sme_id: str) -> dict:
    """Get liquidity position and cash runway analysis"""
    row = financial_df[financial_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No liquidity data found for SME {sme_id}"}
    data = row.iloc[0]

    current_ratio = float(data['current_ratio'])
    cash_runway   = float(data['cash_runway_months'])

    return {
        "sme_id": sme_id,
        "current_ratio": round(current_ratio, 2),
        "cash_runway_months": round(cash_runway, 1),
        "liquidity_rating": _rate_liquidity(current_ratio, cash_runway),
        "solvency_assessment": _assess_solvency(current_ratio, cash_runway),
        "risk_level": _liquidity_risk_level(current_ratio, cash_runway),
    }


@mcp.tool()
def get_leverage_analysis(sme_id: str) -> dict:
    """Get leverage ratios and debt sustainability analysis"""
    row = financial_df[financial_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No leverage data found for SME {sme_id}"}
    data = row.iloc[0]

    debt_to_equity    = float(data['debt_to_equity'])
    interest_coverage = float(data['interest_coverage'])

    return {
        "sme_id": sme_id,
        "debt_to_equity": round(debt_to_equity, 2),
        "interest_coverage": round(interest_coverage, 2),
        "leverage_rating": _rate_leverage(debt_to_equity, interest_coverage),
        "debt_sustainability": _assess_debt_sustainability(debt_to_equity, interest_coverage),
        "risk_level": _leverage_risk_level(debt_to_equity, interest_coverage),
    }


@mcp.tool()
def assess_financial_health(sme_id: str) -> dict:
    """Overall financial health assessment"""
    row = financial_df[financial_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No financial data found for SME {sme_id}"}
    data = row.iloc[0]

    health_score = _calculate_financial_health_score(data)
    concerns     = _identify_financial_concerns(data)

    return {
        "sme_id": sme_id,
        "financial_health_score": round(health_score, 1),
        "health_rating": _rate_financial_health(health_score),
        "revenue_growth_yoy": f"{float(data['revenue_growth_yoy']):.1f}%",
        "ebitda_margin": f"{float(data['ebitda_margin']) * 100:.1f}%",
        "current_ratio": round(float(data['current_ratio']), 2),
        "debt_to_equity": round(float(data['debt_to_equity']), 2),
        "cash_runway_months": round(float(data['cash_runway_months']), 1),
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_financial_risk_points(health_score)} points to overall risk score",
    }


# ===========================================================================
# LINKEDIN / EMPLOYEE TOOLS
# (from linkedin_server.py — port 8003)
# ===========================================================================

@mcp.tool()
def get_employee_count(sme_id: str) -> dict:
    """Get current employee count and hiring trends for an SME"""
    row = employees_df[employees_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No employee data found for SME {sme_id}"}
    data = row.iloc[0]
    return {
        "sme_id": sme_id,
        "current_employee_count": int(data['employee_count']),
        "trend": data['trend'],
        "change_30d": int(data['change_30d']),
        "change_90d": int(data['change_90d']),
        "hiring_active": bool(data['hiring_active']),
        "last_updated": data['last_updated'],
    }


@mcp.tool()
def get_employee_trend(sme_id: str) -> dict:
    """Get employee growth/decline trend over 30 and 90 days"""
    row = employees_df[employees_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No trend data found for SME {sme_id}"}
    data = row.iloc[0]

    current       = int(data['employee_count'])
    change_30d    = int(data['change_30d'])
    change_90d    = int(data['change_90d'])
    count_30d_ago = current - change_30d
    count_90d_ago = current - change_90d

    return {
        "current_count": current,
        "count_30_days_ago": count_30d_ago,
        "count_90_days_ago": count_90d_ago,
        "change_30d": change_30d,
        "change_90d": change_90d,
        "pct_change_30d": round((change_30d / count_30d_ago * 100), 1) if count_30d_ago > 0 else 0,
        "pct_change_90d": round((change_90d / count_90d_ago * 100), 1) if count_90d_ago > 0 else 0,
        "trend_direction": data['trend'],
        "interpretation": _interpret_employee_trend(change_30d, change_90d),
    }


@mcp.tool()
def get_recent_departures(sme_id: str, days: int = 90) -> dict:
    """Get list of recent employee departures, especially senior staff"""
    dept = departures_df[departures_df['sme_id'] == sme_id].copy()
    if dept.empty:
        return {"info": f"No departures recorded for SME {sme_id}"}

    cutoff = datetime.now() - pd.Timedelta(days=days)
    recent = dept[dept['left_date'] >= cutoff]
    if recent.empty:
        return {"info": f"No departures in last {days} days for SME {sme_id}"}

    departure_list = [
        {
            "name": row['employee_name'],
            "title": row['title'],
            "seniority": row['seniority'],
            "tenure_months": int(row['tenure_months']),
            "left_date": row['left_date'].strftime('%Y-%m-%d'),
            "reason": row['reason'],
            "replacement_hired": bool(row['replacement_hired']),
        }
        for _, row in recent.iterrows()
    ]

    c_level_n  = len(recent[recent['seniority'] == 'C-Level'])
    vp_n       = len(recent[recent['seniority'] == 'VP'])
    unreplaced = len(recent[recent['replacement_hired'] == False])

    return {
        "total_departures": len(recent),
        "c_level_departures": c_level_n,
        "vp_departures": vp_n,
        "unreplaced_positions": unreplaced,
        "risk_level": _assess_departure_risk(c_level_n, vp_n, unreplaced),
        "departures": departure_list,
    }


@mcp.tool()
def check_hiring_activity(sme_id: str) -> dict:
    """Check if company is actively hiring (indicator of growth or distress)"""
    row = employees_df[employees_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No hiring data found for SME {sme_id}"}
    data = row.iloc[0]

    is_hiring  = bool(data['hiring_active'])
    change_30d = int(data['change_30d'])

    return {
        "sme_id": sme_id,
        "actively_hiring": is_hiring,
        "recent_hires_30d": max(0, change_30d),
        "trend": data['trend'],
        "interpretation": _interpret_hiring(is_hiring, change_30d),
    }


# ===========================================================================
# NEWS INTELLIGENCE TOOLS
# ===========================================================================

@mcp.tool()
def get_recent_events(sme_id: str, days: int = 90) -> dict:
    """Get recent news events for an SME"""
    cutoff = datetime.now() - timedelta(days=days)
    events = news_df[
        (news_df['sme_id'] == sme_id) &
        (news_df['event_date'] >= cutoff)
    ].sort_values('event_date', ascending=False)

    if events.empty:
        return {"info": f"No news events found for SME {sme_id} in last {days} days"}

    events_list = [
        {
            "date": row['event_date'].strftime('%Y-%m-%d'),
            "type": row['event_type'],
            "severity": row['severity'],
            "title": row['title'],
            "summary": row['summary'],
            "source": row['source'],
            "sentiment_score": round(float(row['sentiment_score']), 2),
            "impact_score": int(row['impact_score']),
            "verified": bool(row['verified']),
        }
        for _, row in events.iterrows()
    ]

    return {
        "sme_id": sme_id,
        "total_events": len(events),
        "critical_events": len(events[events['severity'] == 'critical']),
        "avg_sentiment": round(float(events['sentiment_score'].mean()), 2),
        "events": events_list,
    }


@mcp.tool()
def get_sentiment_analysis(sme_id: str, days: int = 30) -> dict:
    """Get sentiment analysis for recent news coverage"""
    cutoff = datetime.now() - timedelta(days=days)
    events = news_df[
        (news_df['sme_id'] == sme_id) &
        (news_df['event_date'] >= cutoff)
    ]

    if events.empty:
        return {"info": f"No news events for sentiment analysis for SME {sme_id}"}

    avg_sentiment = float(events['sentiment_score'].mean())
    avg_impact    = float(events['impact_score'].mean())

    return {
        "sme_id": sme_id,
        "period_days": days,
        "event_count": len(events),
        "avg_sentiment_score": round(avg_sentiment, 2),
        "avg_impact_score": round(avg_impact, 1),
        "sentiment_rating": _rate_sentiment(avg_sentiment),
        "sentiment_trend": _calculate_sentiment_trend(events),
        "negative_events": len(events[events['sentiment_score'] < -0.3]),
        "positive_events": len(events[events['sentiment_score'] > 0.3]),
    }


@mcp.tool()
def assess_news_risk(sme_id: str) -> dict:
    """Comprehensive news-based risk assessment"""
    cutoff_30 = datetime.now() - timedelta(days=30)
    cutoff_90 = datetime.now() - timedelta(days=90)

    events_30 = news_df[(news_df['sme_id'] == sme_id) & (news_df['event_date'] >= cutoff_30)]
    events_90 = news_df[(news_df['sme_id'] == sme_id) & (news_df['event_date'] >= cutoff_90)]

    if events_90.empty:
        return {"info": f"No news events found for SME {sme_id} — insufficient data for risk assessment"}

    risk_score   = _calculate_news_risk_score(events_30, events_90)
    risk_factors = _identify_news_risk_factors(events_30, events_90)

    return {
        "sme_id": sme_id,
        "news_risk_score": round(risk_score, 1),
        "risk_rating": _rate_news_risk(risk_score),
        "events_30d": len(events_30),
        "events_90d": len(events_90),
        "critical_events_30d": len(events_30[events_30['severity'] == 'critical']),
        "avg_sentiment_30d": round(events_30['sentiment_score'].mean(), 2) if len(events_30) > 0 else 0,
        "avg_impact_30d": round(events_30['impact_score'].mean(), 1) if len(events_30) > 0 else 0,
        "key_risk_factors": risk_factors,
        "risk_contribution": f"Adds {_news_risk_points(risk_score)} points to overall risk score",
    }


# ===========================================================================
# PAYMENT DATA TOOLS
# ===========================================================================

@mcp.tool()
def get_payment_behavior(sme_id: str) -> dict:
    """Get payment behavior and late payment trends"""
    row = smes_df[smes_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No payment data found for SME {sme_id}"}
    data = row.iloc[0]

    late_payments = int(data['late_payments_6m'])
    avg_days_late = int(data['avg_days_late'])

    return {
        "sme_id": sme_id,
        "days_payable_outstanding": int(data['days_payable_outstanding']),
        "late_payments_6m": late_payments,
        "avg_days_late": avg_days_late,
        "payment_behavior_rating": _rate_payment_behavior(late_payments, avg_days_late),
        "payment_risk_level": _assess_payment_risk(late_payments, avg_days_late),
    }


@mcp.tool()
def get_transaction_volume(sme_id: str) -> dict:
    """Get transaction volume trends"""
    row = smes_df[smes_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No transaction data found for SME {sme_id}"}
    data = row.iloc[0]

    current_monthly  = int(data['transaction_volume_q4']) / 3
    previous_monthly = int(data['transaction_volume_q3']) / 3
    pct_change = ((current_monthly - previous_monthly) / previous_monthly * 100) if previous_monthly > 0 else 0

    return {
        "sme_id": sme_id,
        "transaction_volume_q4": int(data['transaction_volume_q4']),
        "transaction_volume_q3": int(data['transaction_volume_q3']),
        "avg_monthly_current": round(current_monthly),
        "avg_monthly_previous": round(previous_monthly),
        "pct_change_qoq": round(pct_change, 1),
        "volume_trend": _assess_volume_trend(pct_change),
        "velocity_rating": _rate_transaction_velocity(current_monthly, pct_change),
    }


@mcp.tool()
def get_payment_health(sme_id: str) -> dict:
    """Overall payment health assessment"""
    row = smes_df[smes_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No payment health data found for SME {sme_id}"}
    data = row.iloc[0]

    late_payments = int(data['late_payments_6m'])
    avg_days_late = int(data['avg_days_late'])
    dpo           = int(data['days_payable_outstanding'])
    health_score  = _calculate_payment_health_score(late_payments, avg_days_late, dpo)
    concerns      = _identify_payment_concerns(late_payments, avg_days_late, dpo)

    return {
        "sme_id": sme_id,
        "payment_health_score": round(health_score, 1),
        "health_rating": _rate_payment_health(health_score),
        "late_payments_6m": late_payments,
        "avg_days_late": avg_days_late,
        "days_payable_outstanding": dpo,
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_payment_risk_points(health_score)} points to overall risk score",
    }


@mcp.tool()
def check_payment_stress_signals(sme_id: str) -> dict:
    """Detect payment stress signals (extending payment terms, late patterns)"""
    row = smes_df[smes_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No payment stress data found for SME {sme_id}"}
    data = row.iloc[0]

    late_payments = int(data['late_payments_6m'])
    avg_days_late = int(data['avg_days_late'])
    dpo           = int(data['days_payable_outstanding'])

    stress_signals = []
    if late_payments >= 5:
        stress_signals.append(f"Frequent late payments: {late_payments} in 6 months")
    if avg_days_late > 15:
        stress_signals.append(f"Significantly late on average: {avg_days_late} days")
    if dpo > 60:
        stress_signals.append(f"Extended payment terms: DPO {dpo} days")

    stress_level = "HIGH" if len(stress_signals) >= 2 else ("MEDIUM" if stress_signals else "LOW")

    return {
        "sme_id": sme_id,
        "stress_level": stress_level,
        "stress_signals": stress_signals,
        "late_payments_6m": late_payments,
        "avg_days_late": avg_days_late,
        "days_payable_outstanding": dpo,
    }


# ===========================================================================
# WEB TRAFFIC TOOLS
# ===========================================================================

@mcp.tool()
def get_traffic_metrics(sme_id: str) -> dict:
    """Get website traffic metrics and trends"""
    row = traffic_df[traffic_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No traffic data found for SME {sme_id}"}
    data = row.iloc[0]
    return {
        "sme_id": sme_id,
        "monthly_visitors": int(data['users_monthly']),
        "sessions_monthly": int(data['sessions_monthly']),
        "traffic_change_qoq": f"{float(data['users_change_qoq']):.1f}%",
        "bounce_rate": f"{float(data['bounce_rate']) * 100:.1f}%",
        "avg_session_duration_seconds": int(data['avg_session_duration_sec']),
        "conversion_rate": f"{float(data['conversion_rate']):.2f}%",
        "top_source": data['top_source'],
    }


@mcp.tool()
def get_traffic_trend(sme_id: str) -> dict:
    """Analyse traffic trends quarter-on-quarter"""
    row = traffic_df[traffic_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No trend data found for SME {sme_id}"}
    data = row.iloc[0]

    current_visitors = int(data['users_monthly'])
    change_qoq       = float(data['users_change_qoq'])
    visitors_prev    = int(current_visitors / (1 + change_qoq / 100)) if change_qoq != -100 else 0

    return {
        "sme_id": sme_id,
        "current_monthly_visitors": current_visitors,
        "visitors_previous_period": visitors_prev,
        "change_qoq": f"{change_qoq:.1f}%",
        "trend_direction": _assess_traffic_trend(change_qoq),
        "traffic_health": _rate_traffic_health(current_visitors, change_qoq),
    }


@mcp.tool()
def get_engagement_metrics(sme_id: str) -> dict:
    """Get user engagement metrics (bounce rate, session duration)"""
    row = traffic_df[traffic_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No engagement data found for SME {sme_id}"}
    data = row.iloc[0]

    bounce_rate      = float(data['bounce_rate']) * 100
    session_duration = int(data['avg_session_duration_sec'])

    return {
        "sme_id": sme_id,
        "bounce_rate": f"{bounce_rate:.1f}%",
        "avg_session_duration": f"{session_duration // 60}m {session_duration % 60}s",
        "conversion_rate": f"{float(data['conversion_rate']):.2f}%",
        "engagement_rating": _rate_engagement(bounce_rate, session_duration),
        "engagement_health": _assess_engagement_health(bounce_rate, session_duration),
    }


@mcp.tool()
def assess_digital_presence(sme_id: str) -> dict:
    """Overall digital presence and web health assessment"""
    row = traffic_df[traffic_df['sme_id'] == sme_id]
    if row.empty:
        return {"error": f"No digital presence data found for SME {sme_id}"}
    data = row.iloc[0]

    presence_score = _calculate_digital_presence_score(data)
    concerns       = _identify_digital_concerns(data)

    return {
        "sme_id": sme_id,
        "digital_presence_score": round(presence_score, 1),
        "presence_rating": _rate_digital_presence(presence_score),
        "monthly_visitors": int(data['users_monthly']),
        "traffic_change_qoq": f"{float(data['users_change_qoq']):.1f}%",
        "bounce_rate": f"{float(data['bounce_rate']) * 100:.1f}%",
        "conversion_rate": f"{float(data['conversion_rate']):.2f}%",
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_digital_risk_points(presence_score)} points to overall risk score",
    }


# ===========================================================================
# HELPER FUNCTIONS — Companies House
# ===========================================================================

def _assess_compliance(overdue: bool, days: int, ccjs: int, insolvency: bool) -> str:
    if insolvency:                   return "🔴 CRITICAL: Insolvency proceedings active"
    elif overdue and days > 90:      return "🔴 CRITICAL: Accounts severely overdue"
    elif ccjs >= 3:                  return "🟠 HIGH RISK: Multiple County Court Judgements"
    elif overdue and days > 30:      return "🟡 WARNING: Accounts overdue"
    elif ccjs > 0:                   return "⚠️ CAUTION: CCJ on record"
    return "✅ COMPLIANT: All filings up to date"


def _compliance_risk_level(overdue: bool, days: int, ccjs: int, insolvency: bool) -> str:
    if insolvency:                           return "CRITICAL"
    elif (overdue and days > 90) or ccjs >= 3: return "HIGH"
    elif (overdue and days > 30) or ccjs >= 2: return "MEDIUM"
    elif overdue or ccjs > 0:               return "LOW"
    return "MINIMAL"


def _assess_director_stability(changes: int, current: int) -> str:
    if changes >= 3:   return "🔴 UNSTABLE: High turnover in boardroom"
    elif changes >= 2: return "🟡 WATCH: Notable director changes"
    elif changes >= 1: return "⚠️ MONITOR: Director change recorded"
    return "✅ STABLE: No director changes in 12 months"


def _calculate_corporate_health_score(overdue, days, ccjs, insolvency, dir_changes, status) -> float:
    score = 5
    if insolvency:        score += 60
    if overdue:           score += min(30, days / 3)
    score += min(25, ccjs * 8)
    if dir_changes >= 3:  score += 20
    elif dir_changes >= 2:score += 10
    if status.lower() != 'active': score += 15
    return min(score, 100)


def _rate_corporate_health(score: float) -> str:
    if score < 20:   return "Excellent (Minimal Risk)"
    elif score < 35: return "Good (Low Risk)"
    elif score < 50: return "Fair (Medium Risk)"
    elif score < 70: return "Poor (High Risk)"
    return "Critical (Very High Risk)"


def _identify_corporate_concerns(overdue, days, ccjs, insolvency, dir_changes) -> list:
    concerns = []
    if insolvency:         concerns.append("Active insolvency proceedings")
    if overdue:            concerns.append(f"Accounts {'severely ' if days > 90 else ''}overdue ({days} days)")
    if ccjs >= 3:          concerns.append(f"Multiple CCJs ({ccjs})")
    elif ccjs > 0:         concerns.append(f"{ccjs} County Court Judgement(s)")
    if dir_changes >= 3:   concerns.append(f"Frequent director changes ({dir_changes} in 12m)")
    elif dir_changes >= 2: concerns.append(f"Multiple director changes ({dir_changes} in 12m)")
    return concerns


def _corporate_risk_points(score: float) -> str:
    if score < 25:   return "5-10"
    elif score < 40: return "10-20"
    elif score < 60: return "20-35"
    elif score < 80: return "35-50"
    return "50-70"


# ===========================================================================
# HELPER FUNCTIONS — Financial
# ===========================================================================

def _assess_revenue_trend(q1, q2, q3, q4) -> str:
    quarters = [q1, q2, q3, q4]
    growing  = all(quarters[i] <= quarters[i+1] for i in range(3))
    declining= all(quarters[i] >= quarters[i+1] for i in range(3))
    if growing:
        rate = ((q4 - q1) / q1 * 100) if q1 > 0 else 0
        return f"📈 Consistently Growing ({rate:.1f}% Q1→Q4)"
    elif declining:
        rate = ((q1 - q4) / q1 * 100) if q1 > 0 else 0
        return f"📉 Consistently Declining (-{rate:.1f}% Q1→Q4)"
    return "↕️ Volatile (Mixed growth/decline)"


def _assess_revenue_volatility(quarters: list) -> str:
    if len(quarters) < 2: return "Insufficient data"
    mean  = statistics.mean(quarters)
    stdev = statistics.stdev(quarters)
    cv    = (stdev / mean * 100) if mean > 0 else 0
    if cv < 5:    return "Very Stable (Low volatility)"
    elif cv < 10: return "Stable (Normal volatility)"
    elif cv < 20: return "Moderate (Some volatility)"
    return "High (Significant volatility)"


def _rate_liquidity(current_ratio: float, cash_runway: float) -> str:
    if current_ratio >= 2.0 and cash_runway >= 12: return "Excellent"
    elif current_ratio >= 1.5 and cash_runway >= 9: return "Good"
    elif current_ratio >= 1.2 and cash_runway >= 6: return "Adequate"
    elif current_ratio >= 1.0 and cash_runway >= 3: return "Weak"
    return "Critical"


def _assess_solvency(current_ratio: float, cash_runway: float) -> str:
    if current_ratio < 1.0:  return "🔴 CRITICAL: Current liabilities exceed assets"
    elif cash_runway < 3:    return "🔴 CRITICAL: Less than 3 months cash runway"
    elif cash_runway < 6:    return "🟡 WARNING: Limited cash runway (< 6 months)"
    return "✅ HEALTHY: Adequate liquidity"


def _liquidity_risk_level(current_ratio: float, cash_runway: float) -> str:
    if current_ratio < 1.0 or cash_runway < 3:   return "CRITICAL"
    elif current_ratio < 1.2 or cash_runway < 6: return "HIGH"
    elif current_ratio < 1.5 or cash_runway < 9: return "MEDIUM"
    return "LOW"


def _rate_leverage(debt_to_equity: float, interest_coverage: float) -> str:
    if debt_to_equity <= 0.5 and interest_coverage >= 5:   return "Excellent"
    elif debt_to_equity <= 1.0 and interest_coverage >= 3: return "Good"
    elif debt_to_equity <= 1.5 and interest_coverage >= 2: return "Adequate"
    elif debt_to_equity <= 2.0 and interest_coverage >= 1: return "Weak"
    return "Critical"


def _assess_debt_sustainability(debt_to_equity: float, interest_coverage: float) -> str:
    if interest_coverage < 1.0:                              return "🔴 CRITICAL: Cannot cover interest payments"
    elif interest_coverage < 1.5 or debt_to_equity > 3.0:   return "🟠 HIGH RISK: Debt levels unsustainable"
    elif interest_coverage < 2.5 or debt_to_equity > 1.5:   return "🟡 CAUTION: Elevated leverage"
    return "✅ SUSTAINABLE: Manageable debt levels"


def _leverage_risk_level(debt_to_equity: float, interest_coverage: float) -> str:
    if interest_coverage < 1.0:                              return "CRITICAL"
    elif interest_coverage < 1.5 or debt_to_equity > 3.0:   return "HIGH"
    elif interest_coverage < 2.5 or debt_to_equity > 1.5:   return "MEDIUM"
    return "LOW"


def _calculate_financial_health_score(data: pd.Series) -> float:
    score          = 10
    growth_yoy     = float(data['revenue_growth_yoy'])
    ebitda_margin  = float(data['ebitda_margin']) * 100
    current_ratio  = float(data['current_ratio'])
    cash_runway    = float(data['cash_runway_months'])
    debt_to_equity = float(data['debt_to_equity'])
    interest_cov   = float(data['interest_coverage'])

    if growth_yoy < -10:    score += 30
    elif growth_yoy < -5:   score += 20
    elif growth_yoy < 0:    score += 10
    elif growth_yoy < 5:    score += 5

    if ebitda_margin < 5:   score += 30
    elif ebitda_margin < 10:score += 20
    elif ebitda_margin < 15:score += 10

    if current_ratio < 1.0 or cash_runway < 3:   score += 40
    elif current_ratio < 1.2 or cash_runway < 6: score += 25
    elif current_ratio < 1.5 or cash_runway < 9: score += 15

    if interest_cov < 1.0:   score += 35
    elif interest_cov < 1.5: score += 25
    elif interest_cov < 2.0: score += 15

    if debt_to_equity > 3.0:  score += 25
    elif debt_to_equity > 2.0:score += 15
    elif debt_to_equity > 1.5:score += 8

    return min(score, 100)


def _rate_financial_health(score: float) -> str:
    if score < 25:   return "Excellent (Very Low Risk)"
    elif score < 40: return "Good (Low Risk)"
    elif score < 60: return "Fair (Medium Risk)"
    elif score < 75: return "Poor (High Risk)"
    return "Critical (Very High Risk)"


def _identify_financial_concerns(data: pd.Series) -> list:
    concerns       = []
    growth_yoy     = float(data['revenue_growth_yoy'])
    ebitda_margin  = float(data['ebitda_margin']) * 100
    current_ratio  = float(data['current_ratio'])
    cash_runway    = float(data['cash_runway_months'])
    interest_cov   = float(data['interest_coverage'])
    debt_to_equity = float(data['debt_to_equity'])

    if growth_yoy < -10:      concerns.append(f"Severe revenue decline ({growth_yoy:.1f}% YoY)")
    elif growth_yoy < -5:     concerns.append(f"Significant revenue decline ({growth_yoy:.1f}% YoY)")
    if ebitda_margin < 5:     concerns.append(f"Very low EBITDA margin ({ebitda_margin:.1f}%)")
    elif ebitda_margin < 10:  concerns.append(f"Low EBITDA margin ({ebitda_margin:.1f}%)")
    if current_ratio < 1.0:   concerns.append(f"Current ratio below 1.0 ({current_ratio:.2f})")
    if cash_runway < 3:       concerns.append(f"Critical cash runway ({cash_runway:.1f} months)")
    elif cash_runway < 6:     concerns.append(f"Limited cash runway ({cash_runway:.1f} months)")
    if interest_cov < 1.0:   concerns.append(f"Interest coverage below 1.0 ({interest_cov:.2f})")
    elif interest_cov < 1.5: concerns.append(f"Low interest coverage ({interest_cov:.2f})")
    if debt_to_equity > 3.0:  concerns.append(f"Very high debt-to-equity ({debt_to_equity:.2f})")
    elif debt_to_equity > 2.0:concerns.append(f"High debt-to-equity ({debt_to_equity:.2f})")
    return concerns


def _financial_risk_points(score: float) -> str:
    if score < 30:   return "10-20"
    elif score < 50: return "20-35"
    elif score < 70: return "35-55"
    return "55-80"


# ===========================================================================
# HELPER FUNCTIONS — LinkedIn
# ===========================================================================

def _interpret_employee_trend(change_30d: int, change_90d: int) -> str:
    if change_90d < -10:  return "🔴 CRITICAL: Mass layoffs detected (>10 employees in 90d)"
    elif change_90d < -5: return "🟠 WARNING: Significant downsizing (5-10 employees in 90d)"
    elif change_30d < -3: return "🟡 CAUTION: Recent layoffs detected (>3 in 30d)"
    elif change_90d < 0:  return "⚠️ WATCH: Slow decline in headcount"
    elif change_90d < 5:  return "✅ STABLE: Minimal change in headcount"
    return "🟢 POSITIVE: Growing headcount (hiring)"


def _assess_departure_risk(c_level: int, vp_level: int, unreplaced: int) -> str:
    if c_level >= 2 or (c_level >= 1 and vp_level >= 2): return "CRITICAL"
    elif c_level >= 1 or vp_level >= 2:                   return "HIGH"
    elif vp_level >= 1 or unreplaced >= 3:                return "MEDIUM"
    return "LOW"


def _interpret_hiring(is_hiring: bool, change_30d: int) -> str:
    if is_hiring and change_30d > 3:   return "🟢 POSITIVE: Active hiring indicates growth/expansion"
    elif is_hiring and change_30d > 0: return "✅ STABLE: Modest hiring for replacement/growth"
    elif is_hiring:                    return "⚠️ WATCH: Hiring but headcount declining (high turnover?)"
    return "🔴 WARNING: No active hiring (cost-cutting or limited growth)"


# ===========================================================================
# HELPER FUNCTIONS — News
# ===========================================================================

def _calculate_sentiment_trend(events: pd.DataFrame) -> str:
    if len(events) < 3: return "Insufficient data"
    sorted_e   = events.sort_values('event_date')
    mid        = len(sorted_e) // 2
    first_avg  = sorted_e.iloc[:mid]['sentiment_score'].mean()
    second_avg = sorted_e.iloc[mid:]['sentiment_score'].mean()
    diff = second_avg - first_avg
    if diff > 0.2:    return "📈 Improving (Sentiment getting more positive)"
    elif diff < -0.2: return "📉 Deteriorating (Sentiment getting more negative)"
    return "➡️ Stable (No significant trend)"


def _rate_sentiment(score: float) -> str:
    if score > 0.6:    return "Very Positive"
    elif score > 0.2:  return "Positive"
    elif score >= -0.2:return "Neutral"
    elif score >= -0.6:return "Negative"
    return "Very Negative"


def _calculate_news_risk_score(events_30: pd.DataFrame, events_90: pd.DataFrame) -> float:
    score = 0
    if len(events_30) > 0:
        critical      = len(events_30[events_30['severity'] == 'critical'])
        score        += critical * 20
        avg_sentiment = events_30['sentiment_score'].mean()
        if avg_sentiment < -0.5:   score += 30
        elif avg_sentiment < -0.3: score += 20
        elif avg_sentiment < 0:    score += 10
    if len(events_90) > 0:
        avg_impact = events_90['impact_score'].mean()
        score += min(20, avg_impact * 2)
    return min(score, 100)


def _rate_news_risk(score: float) -> str:
    if score < 25:   return "Low (Positive/Neutral coverage)"
    elif score < 40: return "Low-Medium (Some concerns)"
    elif score < 60: return "Medium (Notable negative coverage)"
    elif score < 75: return "High (Significant negative events)"
    return "Critical (Multiple severe events)"


def _identify_news_risk_factors(events_30: pd.DataFrame, events_90: pd.DataFrame) -> list:
    factors = []
    critical_30 = len(events_30[events_30['severity'] == 'critical'])
    if critical_30 >= 3:   factors.append(f"Multiple critical events in last 30 days ({critical_30})")
    elif critical_30 >= 1: factors.append("Critical event in last 30 days")

    litigation = len(events_30[events_30['event_type'].isin(['litigation', 'compliance'])])
    if litigation > 0: factors.append(f"Legal/compliance issues ({litigation} events)")

    departures = len(events_30[events_30['event_type'] == 'departure'])
    if departures >= 2: factors.append(f"Multiple departures reported ({departures})")

    if len(events_30) > 0:
        if events_30['sentiment_score'].mean() < -0.5:
            factors.append("Predominantly negative media coverage")

    cust_issues = len(events_30[events_30['event_type'].isin(['customer_loss', 'reputation'])])
    if cust_issues > 0: factors.append(f"Customer/reputation concerns ({cust_issues} events)")
    return factors


def _news_risk_points(score: float) -> str:
    if score < 30:   return "5-15"
    elif score < 50: return "15-30"
    elif score < 70: return "30-50"
    return "50-95"


# ===========================================================================
# HELPER FUNCTIONS — Payment
# ===========================================================================

def _rate_payment_behavior(late_payments: int, avg_days_late: int) -> str:
    if late_payments == 0:                           return "Excellent"
    elif late_payments <= 1 and avg_days_late <= 5:  return "Good"
    elif late_payments <= 3 and avg_days_late <= 10: return "Fair"
    elif late_payments <= 5 and avg_days_late <= 15: return "Poor"
    return "Critical"


def _assess_payment_risk(late_payments: int, avg_days_late: int) -> str:
    if late_payments >= 8 or avg_days_late > 20:   return "CRITICAL"
    elif late_payments >= 5 or avg_days_late > 15: return "HIGH"
    elif late_payments >= 3 or avg_days_late > 10: return "MEDIUM"
    elif late_payments >= 1 or avg_days_late > 5:  return "LOW"
    return "MINIMAL"


def _assess_volume_trend(pct_change: float) -> str:
    if pct_change < -20:   return "🔴 CRITICAL: Severe volume decline"
    elif pct_change < -10: return "🟠 WARNING: Significant volume decline"
    elif pct_change < 0:   return "⚠️ WATCH: Slight decline"
    elif pct_change < 10:  return "✅ STABLE: Flat to modest growth"
    return "🟢 POSITIVE: Strong volume growth"


def _rate_transaction_velocity(monthly_vol: float, pct_change: float) -> str:
    if monthly_vol < 100 or pct_change < -20:   return "Critical"
    elif monthly_vol < 300 or pct_change < -10: return "Poor"
    elif monthly_vol < 500 or pct_change < 0:   return "Fair"
    elif monthly_vol < 1000:                    return "Good"
    return "Excellent"


def _calculate_payment_health_score(late_payments: int, avg_days_late: int, dpo: int) -> float:
    score  = 5
    score += min(40, late_payments * 6)
    score += min(30, avg_days_late * 1.5)
    if dpo > 90:    score += 25
    elif dpo > 60:  score += 15
    elif dpo > 45:  score += 8
    return min(score, 100)


def _rate_payment_health(score: float) -> str:
    if score < 20:   return "Excellent"
    elif score < 35: return "Good"
    elif score < 55: return "Fair"
    elif score < 75: return "Poor"
    return "Critical"


def _identify_payment_concerns(late_payments: int, avg_days_late: int, dpo: int) -> list:
    concerns = []
    if late_payments >= 8:    concerns.append(f"Very high late payment frequency ({late_payments} in 6m)")
    elif late_payments >= 5:  concerns.append(f"High late payment frequency ({late_payments} in 6m)")
    elif late_payments >= 3:  concerns.append(f"Moderate late payments ({late_payments} in 6m)")
    if avg_days_late > 20:    concerns.append(f"Significantly late on average ({avg_days_late} days)")
    elif avg_days_late > 10:  concerns.append(f"Consistently late ({avg_days_late} days average)")
    if dpo > 90:   concerns.append(f"Very extended payment terms (DPO: {dpo} days)")
    elif dpo > 60: concerns.append(f"Extended payment terms (DPO: {dpo} days)")
    return concerns


def _payment_risk_points(score: float) -> str:
    if score < 25:   return "3-8"
    elif score < 45: return "8-18"
    elif score < 65: return "18-30"
    return "30-45"


# ===========================================================================
# HELPER FUNCTIONS — Web Traffic
# ===========================================================================

def _assess_traffic_trend(change_qoq: float) -> str:
    if change_qoq < -30:   return "🔴 CRITICAL: Severe traffic decline (>-30% QoQ)"
    elif change_qoq < -15: return "🟠 WARNING: Significant traffic decline"
    elif change_qoq < 0:   return "⚠️ WATCH: Gradual traffic decline"
    elif change_qoq < 10:  return "➡️ STABLE: Flat traffic"
    elif change_qoq < 20:  return "✅ POSITIVE: Growing traffic"
    return "🟢 EXCELLENT: Strong growth (>20% QoQ)"


def _rate_traffic_health(visitors: int, change_qoq: float) -> str:
    if visitors < 1000 or change_qoq < -30:   return "Critical"
    elif visitors < 5000 or change_qoq < -15: return "Poor"
    elif visitors < 10000 or change_qoq < 0:  return "Fair"
    elif visitors < 30000:                    return "Good"
    return "Excellent"


def _rate_engagement(bounce_rate: float, session_duration: int) -> str:
    if bounce_rate < 40 and session_duration > 180:  return "Excellent"
    elif bounce_rate < 50 and session_duration > 120:return "Good"
    elif bounce_rate < 60 and session_duration > 60: return "Fair"
    elif bounce_rate < 70 and session_duration > 30: return "Poor"
    return "Critical"


def _assess_engagement_health(bounce_rate: float, session_duration: int) -> str:
    if bounce_rate > 70:        return "🔴 CONCERN: Very high bounce rate indicates poor relevance"
    elif session_duration < 30: return "🟡 WARNING: Very short sessions, low engagement"
    elif bounce_rate > 60:      return "⚠️ WATCH: High bounce rate"
    return "✅ HEALTHY: Reasonable engagement levels"


def _calculate_digital_presence_score(data: pd.Series) -> float:
    score      = 10
    visitors   = int(data['users_monthly'])
    change_qoq = float(data['users_change_qoq'])
    bounce     = float(data['bounce_rate']) * 100
    conv_rate  = float(data['conversion_rate'])

    if visitors < 1000:    score += 35
    elif visitors < 5000:  score += 20
    elif visitors < 10000: score += 10

    if change_qoq < -20:   score += 30
    elif change_qoq < -10: score += 20
    elif change_qoq < 0:   score += 10

    if bounce > 70:        score += 20
    elif bounce > 60:      score += 10

    if conv_rate < 0.5:    score += 15
    elif conv_rate < 1.0:  score += 8

    return min(score, 100)


def _rate_digital_presence(score: float) -> str:
    if score < 25:   return "Excellent (Strong online presence)"
    elif score < 40: return "Good (Solid online presence)"
    elif score < 60: return "Fair (Moderate online presence)"
    elif score < 75: return "Poor (Weak online presence)"
    return "Critical (Very weak online presence)"


def _identify_digital_concerns(data: pd.Series) -> list:
    concerns   = []
    visitors   = int(data['users_monthly'])
    change_qoq = float(data['users_change_qoq'])
    bounce     = float(data['bounce_rate']) * 100
    session    = int(data['avg_session_duration_sec'])
    conv_rate  = float(data['conversion_rate'])

    if visitors < 1000:    concerns.append(f"Very low traffic volume ({visitors:,} monthly visitors)")
    elif visitors < 5000:  concerns.append(f"Low traffic volume ({visitors:,} monthly visitors)")
    if change_qoq < -20:   concerns.append(f"Severe traffic decline ({change_qoq:.1f}% QoQ)")
    elif change_qoq < -10: concerns.append(f"Significant traffic decline ({change_qoq:.1f}% QoQ)")
    if bounce > 70:        concerns.append(f"Very high bounce rate ({bounce:.1f}%)")
    elif bounce > 60:      concerns.append(f"High bounce rate ({bounce:.1f}%)")
    if session < 30:       concerns.append(f"Very short session duration ({session}s)")
    elif session < 60:     concerns.append(f"Short session duration ({session}s)")
    if conv_rate < 0.5:    concerns.append(f"Very low conversion rate ({conv_rate:.2f}%)")
    elif conv_rate < 1.0:  concerns.append(f"Low conversion rate ({conv_rate:.2f}%)")
    return concerns


def _digital_risk_points(score: float) -> str:
    if score < 30:   return "5-10"
    elif score < 50: return "10-20"
    elif score < 70: return "20-35"
    return "35-55"


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001))
    )