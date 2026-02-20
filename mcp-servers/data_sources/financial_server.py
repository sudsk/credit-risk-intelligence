#!/usr/bin/env python3
"""
Financial Data MCP Server - Cloud Run Compatible
Provides quarterly financial statements, ratios, and trend analysis.
"""
import os
import pandas as pd
import statistics
from pathlib import Path
from fastmcp import FastMCP

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
FINANCIAL_CSV = DATA_DIR / "financial_data.csv"

# Load data
financial_df = pd.read_csv(FINANCIAL_CSV)

# Create FastMCP server
mcp = FastMCP("financial-data")


@mcp.tool()
def get_financial_metrics(sme_id: str) -> dict:
    """Get current quarter financial metrics and ratios"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No financial data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    metrics = {
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
        "roe": f"{float(data['roe']) * 100:.1f}%"
    }
    
    return metrics


@mcp.tool()
def get_revenue_trend(sme_id: str) -> dict:
    """Get quarterly revenue trend analysis"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No revenue data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    q1 = int(data['revenue_q1'])
    q2 = int(data['revenue_q2'])
    q3 = int(data['revenue_q3'])
    q4 = int(data['revenue_q4'])
    
    trend = {
        "sme_id": sme_id,
        "q1_revenue": f"€{q1:,}",
        "q2_revenue": f"€{q2:,}",
        "q3_revenue": f"€{q3:,}",
        "q4_revenue": f"€{q4:,}",
        "total_annual": f"€{(q1 + q2 + q3 + q4):,}",
        "yoy_growth": f"{float(data['revenue_growth_yoy']):.1f}%",
        "qoq_growth": f"{float(data['revenue_growth_qoq']):.1f}%",
        "trend_direction": _assess_revenue_trend(q1, q2, q3, q4),
        "volatility": _assess_revenue_volatility([q1, q2, q3, q4])
    }
    
    return trend


@mcp.tool()
def get_liquidity_analysis(sme_id: str) -> dict:
    """Analyze liquidity position (cash runway, current ratio, quick ratio)"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No liquidity data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    current_ratio = float(data['current_ratio'])
    quick_ratio = float(data['quick_ratio'])
    cash_runway = float(data['cash_runway_months'])
    working_capital = int(data['working_capital'])
    
    liquidity = {
        "sme_id": sme_id,
        "current_ratio": round(current_ratio, 2),
        "quick_ratio": round(quick_ratio, 2),
        "cash_runway_months": round(cash_runway, 1),
        "working_capital": f"€{working_capital:,}",
        "liquidity_rating": _rate_liquidity(current_ratio, cash_runway),
        "immediate_solvency": _assess_solvency(current_ratio, cash_runway),
        "risk_level": _liquidity_risk_level(current_ratio, cash_runway)
    }
    
    return liquidity


@mcp.tool()
def get_profitability_analysis(sme_id: str) -> dict:
    """Analyze profitability metrics (margins, ROA, ROE)"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No profitability data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    ebitda_margin = float(data['ebitda_margin']) * 100
    gross_margin = float(data['gross_margin']) * 100
    net_margin = float(data['net_margin']) * 100
    roa = float(data['roa']) * 100
    roe = float(data['roe']) * 100
    
    profitability = {
        "sme_id": sme_id,
        "ebitda_margin": f"{ebitda_margin:.1f}%",
        "gross_margin": f"{gross_margin:.1f}%",
        "net_margin": f"{net_margin:.1f}%",
        "roa": f"{roa:.1f}%",
        "roe": f"{roe:.1f}%",
        "profitability_rating": _rate_profitability(ebitda_margin, net_margin),
        "margin_health": _assess_margin_health(ebitda_margin, gross_margin, net_margin)
    }
    
    return profitability


@mcp.tool()
def get_leverage_analysis(sme_id: str) -> dict:
    """Analyze debt levels and coverage ratios"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No leverage data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    debt_to_equity = float(data['debt_to_equity'])
    interest_coverage = float(data['interest_coverage'])
    
    leverage = {
        "sme_id": sme_id,
        "debt_to_equity": round(debt_to_equity, 2),
        "interest_coverage": round(interest_coverage, 2),
        "leverage_rating": _rate_leverage(debt_to_equity, interest_coverage),
        "debt_sustainability": _assess_debt_sustainability(debt_to_equity, interest_coverage),
        "risk_level": _leverage_risk_level(debt_to_equity, interest_coverage)
    }
    
    return leverage


@mcp.tool()
def assess_financial_health(sme_id: str) -> dict:
    """Overall financial health assessment"""
    fin_row = financial_df[financial_df['sme_id'] == sme_id]
    
    if fin_row.empty:
        return {"error": f"No financial data found for SME {sme_id}"}
    
    data = fin_row.iloc[0]
    
    # Calculate composite financial health score
    health_score = _calculate_financial_health_score(data)
    
    # Identify concerns
    concerns = _identify_financial_concerns(data)
    
    assessment = {
        "sme_id": sme_id,
        "financial_health_score": round(health_score, 1),
        "health_rating": _rate_financial_health(health_score),
        "revenue_growth_yoy": f"{float(data['revenue_growth_yoy']):.1f}%",
        "ebitda_margin": f"{float(data['ebitda_margin']) * 100:.1f}%",
        "current_ratio": round(float(data['current_ratio']), 2),
        "debt_to_equity": round(float(data['debt_to_equity']), 2),
        "cash_runway_months": round(float(data['cash_runway_months']), 1),
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_financial_risk_points(health_score)} points to overall risk score"
    }
    
    return assessment


# Helper functions
def _assess_revenue_trend(q1: int, q2: int, q3: int, q4: int) -> str:
    """Assess revenue trend direction."""
    quarters = [q1, q2, q3, q4]
    
    # Check if consistently growing
    growing = all(quarters[i] <= quarters[i+1] for i in range(3))
    declining = all(quarters[i] >= quarters[i+1] for i in range(3))
    
    if growing:
        growth_rate = ((q4 - q1) / q1 * 100) if q1 > 0 else 0
        return f"📈 Consistently Growing ({growth_rate:.1f}% Q1→Q4)"
    elif declining:
        decline_rate = ((q1 - q4) / q1 * 100) if q1 > 0 else 0
        return f"📉 Consistently Declining (-{decline_rate:.1f}% Q1→Q4)"
    else:
        return "↕️ Volatile (Mixed growth/decline)"


def _assess_revenue_volatility(quarters: list) -> str:
    """Assess revenue volatility."""
    if len(quarters) < 2:
        return "Insufficient data"
    
    mean = statistics.mean(quarters)
    stdev = statistics.stdev(quarters)
    cv = (stdev / mean * 100) if mean > 0 else 0
    
    if cv < 5:
        return "Very Stable (Low volatility)"
    elif cv < 10:
        return "Stable (Normal volatility)"
    elif cv < 20:
        return "Moderate (Some volatility)"
    else:
        return "High (Significant volatility)"


def _rate_liquidity(current_ratio: float, cash_runway: float) -> str:
    """Rate liquidity position."""
    if current_ratio >= 2.0 and cash_runway >= 12:
        return "Excellent"
    elif current_ratio >= 1.5 and cash_runway >= 9:
        return "Good"
    elif current_ratio >= 1.2 and cash_runway >= 6:
        return "Adequate"
    elif current_ratio >= 1.0 and cash_runway >= 3:
        return "Weak"
    else:
        return "Critical"


def _assess_solvency(current_ratio: float, cash_runway: float) -> str:
    """Assess immediate solvency."""
    if current_ratio < 1.0:
        return "🔴 CRITICAL: Current liabilities exceed assets"
    elif cash_runway < 3:
        return "🔴 CRITICAL: Less than 3 months cash runway"
    elif cash_runway < 6:
        return "🟡 WARNING: Limited cash runway (< 6 months)"
    else:
        return "✅ HEALTHY: Adequate liquidity"


def _liquidity_risk_level(current_ratio: float, cash_runway: float) -> str:
    """Determine liquidity risk level."""
    if current_ratio < 1.0 or cash_runway < 3:
        return "CRITICAL"
    elif current_ratio < 1.2 or cash_runway < 6:
        return "HIGH"
    elif current_ratio < 1.5 or cash_runway < 9:
        return "MEDIUM"
    else:
        return "LOW"


def _rate_profitability(ebitda_margin: float, net_margin: float) -> str:
    """Rate profitability."""
    if ebitda_margin >= 25 and net_margin >= 15:
        return "Excellent"
    elif ebitda_margin >= 20 and net_margin >= 10:
        return "Good"
    elif ebitda_margin >= 15 and net_margin >= 5:
        return "Adequate"
    elif ebitda_margin >= 10 and net_margin >= 2:
        return "Weak"
    else:
        return "Poor"


def _assess_margin_health(ebitda: float, gross: float, net: float) -> str:
    """Assess overall margin health."""
    if ebitda < 10:
        return "🔴 CONCERN: Low EBITDA margin indicates operational inefficiency"
    elif net < 3:
        return "🟡 WARNING: Thin net margins, vulnerable to cost increases"
    elif gross < 30:
        return "⚠️ WATCH: Low gross margins limit pricing power"
    else:
        return "✅ HEALTHY: Strong margin profile"


def _rate_leverage(debt_to_equity: float, interest_coverage: float) -> str:
    """Rate leverage position."""
    if debt_to_equity < 1.0 and interest_coverage > 4.0:
        return "Conservative (Low leverage)"
    elif debt_to_equity < 1.5 and interest_coverage > 2.5:
        return "Moderate (Manageable leverage)"
    elif debt_to_equity < 2.0 and interest_coverage > 1.5:
        return "Elevated (High leverage)"
    else:
        return "Aggressive (Very high leverage)"


def _assess_debt_sustainability(debt_to_equity: float, interest_coverage: float) -> str:
    """Assess debt sustainability."""
    if interest_coverage < 1.0:
        return "🔴 UNSUSTAINABLE: Cannot cover interest from operations"
    elif interest_coverage < 1.5 or debt_to_equity > 3.0:
        return "🟠 HIGH RISK: Debt levels concerning"
    elif interest_coverage < 2.0 or debt_to_equity > 2.0:
        return "🟡 MODERATE RISK: Elevated debt levels"
    else:
        return "✅ SUSTAINABLE: Manageable debt levels"


def _leverage_risk_level(debt_to_equity: float, interest_coverage: float) -> str:
    """Determine leverage risk level."""
    if interest_coverage < 1.0:
        return "CRITICAL"
    elif interest_coverage < 1.5 or debt_to_equity > 3.0:
        return "HIGH"
    elif interest_coverage < 2.5 or debt_to_equity > 1.5:
        return "MEDIUM"
    else:
        return "LOW"


def _calculate_financial_health_score(data: pd.Series) -> float:
    """Calculate financial health score (0-100, lower = better)."""
    score = 10  # Base score
    
    # Revenue growth
    growth_yoy = float(data['revenue_growth_yoy'])
    if growth_yoy < -10:
        score += 30
    elif growth_yoy < -5:
        score += 20
    elif growth_yoy < 0:
        score += 10
    elif growth_yoy < 5:
        score += 5
    
    # Profitability
    ebitda_margin = float(data['ebitda_margin']) * 100
    if ebitda_margin < 5:
        score += 30
    elif ebitda_margin < 10:
        score += 20
    elif ebitda_margin < 15:
        score += 10
    
    # Liquidity
    current_ratio = float(data['current_ratio'])
    cash_runway = float(data['cash_runway_months'])
    
    if current_ratio < 1.0 or cash_runway < 3:
        score += 40
    elif current_ratio < 1.2 or cash_runway < 6:
        score += 25
    elif current_ratio < 1.5 or cash_runway < 9:
        score += 15
    
    # Leverage
    debt_to_equity = float(data['debt_to_equity'])
    interest_coverage = float(data['interest_coverage'])
    
    if interest_coverage < 1.0:
        score += 35
    elif interest_coverage < 1.5:
        score += 25
    elif interest_coverage < 2.0:
        score += 15
    
    if debt_to_equity > 3.0:
        score += 25
    elif debt_to_equity > 2.0:
        score += 15
    elif debt_to_equity > 1.5:
        score += 8
    
    return min(score, 100)


def _rate_financial_health(score: float) -> str:
    """Rate financial health."""
    if score < 25:
        return "Excellent (Very Low Risk)"
    elif score < 40:
        return "Good (Low Risk)"
    elif score < 60:
        return "Fair (Medium Risk)"
    elif score < 75:
        return "Poor (High Risk)"
    else:
        return "Critical (Very High Risk)"


def _identify_financial_concerns(data: pd.Series) -> list:
    """Identify financial concerns."""
    concerns = []
    
    # Revenue
    growth_yoy = float(data['revenue_growth_yoy'])
    if growth_yoy < -10:
        concerns.append(f"Severe revenue decline ({growth_yoy:.1f}% YoY)")
    elif growth_yoy < -5:
        concerns.append(f"Significant revenue decline ({growth_yoy:.1f}% YoY)")
    
    # Profitability
    ebitda_margin = float(data['ebitda_margin']) * 100
    if ebitda_margin < 5:
        concerns.append(f"Very low EBITDA margin ({ebitda_margin:.1f}%)")
    elif ebitda_margin < 10:
        concerns.append(f"Low EBITDA margin ({ebitda_margin:.1f}%)")
    
    # Liquidity
    current_ratio = float(data['current_ratio'])
    cash_runway = float(data['cash_runway_months'])
    
    if current_ratio < 1.0:
        concerns.append(f"Current ratio below 1.0 ({current_ratio:.2f})")
    
    if cash_runway < 3:
        concerns.append(f"Critical cash runway ({cash_runway:.1f} months)")
    elif cash_runway < 6:
        concerns.append(f"Limited cash runway ({cash_runway:.1f} months)")
    
    # Leverage
    interest_coverage = float(data['interest_coverage'])
    if interest_coverage < 1.0:
        concerns.append(f"Interest coverage below 1.0 ({interest_coverage:.2f})")
    elif interest_coverage < 1.5:
        concerns.append(f"Low interest coverage ({interest_coverage:.2f})")
    
    debt_to_equity = float(data['debt_to_equity'])
    if debt_to_equity > 3.0:
        concerns.append(f"Very high debt-to-equity ({debt_to_equity:.2f})")
    elif debt_to_equity > 2.0:
        concerns.append(f"High debt-to-equity ({debt_to_equity:.2f})")
    
    return concerns


def _financial_risk_points(health_score: float) -> str:
    """Map financial health to risk points."""
    if health_score < 30:
        return "10-20"
    elif health_score < 50:
        return "20-35"
    elif health_score < 70:
        return "35-55"
    else:
        return "55-80"


if __name__ == "__main__":
    # Use streamable-http for Cloud Run deployment
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002))
    )