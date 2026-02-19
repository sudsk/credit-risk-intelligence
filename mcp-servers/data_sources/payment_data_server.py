#!/usr/bin/env python3
"""
Payment Data MCP Server - Cloud Run Compatible
Provides payment behavior, late payments, and transaction volume analysis.
"""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastmcp import FastMCP

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
SMES_CSV = DATA_DIR / "smes.csv"

# Load data
smes_df = pd.read_csv(SMES_CSV)

# Create FastMCP server
mcp = FastMCP("payment-data")


@mcp.tool()
def get_payment_behavior(sme_id: str) -> dict:
    """Get payment behavior and late payment trends"""
    sme_row = smes_df[smes_df['sme_id'] == sme_id]
    
    if sme_row.empty:
        return {"error": f"No payment data found for SME {sme_id}"}
    
    data = sme_row.iloc[0]
    
    behavior = {
        "sme_id": sme_id,
        "days_payable_outstanding": int(data['days_payable_outstanding']),
        "late_payments_6m": int(data['late_payments_6m']),
        "avg_days_late": int(data['avg_days_late']),
        "payment_behavior_rating": _rate_payment_behavior(
            int(data['late_payments_6m']),
            int(data['avg_days_late'])
        ),
        "payment_risk_level": _assess_payment_risk(
            int(data['late_payments_6m']),
            int(data['avg_days_late'])
        )
    }
    
    return behavior


@mcp.tool()
def get_transaction_volume(sme_id: str) -> dict:
    """Get transaction volume trends"""
    sme_row = smes_df[smes_df['sme_id'] == sme_id]
    
    if sme_row.empty:
        return {"error": f"No transaction data found for SME {sme_id}"}
    
    data = sme_row.iloc[0]
    
    # Calculate monthly volumes from quarterly data
    current_monthly = int(data['transaction_volume_q4']) / 3
    previous_monthly = int(data['transaction_volume_q3']) / 3
    
    pct_change = ((current_monthly - previous_monthly) / previous_monthly * 100) if previous_monthly > 0 else 0
    
    volume = {
        "sme_id": sme_id,
        "transaction_volume_q4": int(data['transaction_volume_q4']),
        "transaction_volume_q3": int(data['transaction_volume_q3']),
        "avg_monthly_current": round(current_monthly),
        "avg_monthly_previous": round(previous_monthly),
        "pct_change_qoq": round(pct_change, 1),
        "volume_trend": _assess_volume_trend(pct_change),
        "velocity_rating": _rate_transaction_velocity(current_monthly, pct_change)
    }
    
    return volume


@mcp.tool()
def get_payment_health(sme_id: str) -> dict:
    """Overall payment health assessment"""
    sme_row = smes_df[smes_df['sme_id'] == sme_id]
    
    if sme_row.empty:
        return {"error": f"No payment health data found for SME {sme_id}"}
    
    data = sme_row.iloc[0]
    
    late_payments = int(data['late_payments_6m'])
    avg_days_late = int(data['avg_days_late'])
    dpo = int(data['days_payable_outstanding'])
    
    # Calculate payment health score
    health_score = _calculate_payment_health_score(late_payments, avg_days_late, dpo)
    
    # Identify concerns
    concerns = _identify_payment_concerns(late_payments, avg_days_late, dpo)
    
    assessment = {
        "sme_id": sme_id,
        "payment_health_score": round(health_score, 1),
        "health_rating": _rate_payment_health(health_score),
        "late_payments_6m": late_payments,
        "avg_days_late": avg_days_late,
        "days_payable_outstanding": dpo,
        "key_concerns": concerns,
        "risk_contribution": f"Adds {_payment_risk_points(health_score)} points to overall risk score"
    }
    
    return assessment


@mcp.tool()
def check_payment_stress_signals(sme_id: str) -> dict:
    """Detect payment stress signals (extending payment terms, late patterns)"""
    sme_row = smes_df[smes_df['sme_id'] == sme_id]
    
    if sme_row.empty:
        return {"error": f"No payment stress data found for SME {sme_id}"}
    
    data = sme_row.iloc[0]
    
    late_payments = int(data['late_payments_6m'])
    avg_days_late = int(data['avg_days_late'])
    dpo = int(data['days_payable_outstanding'])
    
    # Detect stress signals
    stress_signals = []
    severity = "LOW"
    
    if late_payments >= 10:
        stress_signals.append(f"🔴 CRITICAL: {late_payments} late payments in 6 months")
        severity = "CRITICAL"
    elif late_payments >= 5:
        stress_signals.append(f"🟠 HIGH: {late_payments} late payments in 6 months")
        severity = "HIGH" if severity == "LOW" else severity
    elif late_payments >= 3:
        stress_signals.append(f"🟡 MEDIUM: {late_payments} late payments in 6 months")
        severity = "MEDIUM" if severity == "LOW" else severity
    
    if avg_days_late >= 30:
        stress_signals.append(f"🔴 CRITICAL: Average {avg_days_late} days late on payments")
        severity = "CRITICAL"
    elif avg_days_late >= 15:
        stress_signals.append(f"🟠 HIGH: Average {avg_days_late} days late on payments")
        severity = "HIGH" if severity in ["LOW", "MEDIUM"] else severity
    elif avg_days_late >= 7:
        stress_signals.append(f"🟡 MEDIUM: Average {avg_days_late} days late on payments")
        severity = "MEDIUM" if severity == "LOW" else severity
    
    if dpo >= 90:
        stress_signals.append(f"🟠 WARNING: Extended payment terms ({dpo} days)")
        severity = "HIGH" if severity in ["LOW", "MEDIUM"] else severity
    elif dpo >= 75:
        stress_signals.append(f"⚠️ WATCH: Long payment terms ({dpo} days)")
    
    if not stress_signals:
        stress_signals.append("✅ No significant payment stress signals detected")
    
    result = {
        "sme_id": sme_id,
        "stress_level": severity,
        "signals_detected": len([s for s in stress_signals if not s.startswith("✅")]),
        "stress_signals": stress_signals,
        "interpretation": _interpret_payment_stress(severity, late_payments, avg_days_late)
    }
    
    return result


# Helper functions
def _rate_payment_behavior(late_payments: int, avg_days_late: int) -> str:
    """Rate payment behavior."""
    if late_payments == 0:
        return "Excellent (Perfect payment record)"
    elif late_payments <= 2 and avg_days_late <= 5:
        return "Good (Occasional minor delays)"
    elif late_payments <= 5 and avg_days_late <= 15:
        return "Fair (Some late payments)"
    elif late_payments <= 10 and avg_days_late <= 30:
        return "Poor (Frequent late payments)"
    else:
        return "Critical (Severe payment issues)"


def _assess_payment_risk(late_payments: int, avg_days_late: int) -> str:
    """Assess payment risk level."""
    if late_payments >= 10 or avg_days_late >= 30:
        return "CRITICAL"
    elif late_payments >= 5 or avg_days_late >= 15:
        return "HIGH"
    elif late_payments >= 3 or avg_days_late >= 7:
        return "MEDIUM"
    elif late_payments >= 1:
        return "LOW"
    else:
        return "MINIMAL"


def _assess_volume_trend(pct_change: float) -> str:
    """Assess transaction volume trend."""
    if pct_change >= 20:
        return "📈 Strong Growth (>20% increase)"
    elif pct_change >= 10:
        return "📈 Growing (10-20% increase)"
    elif pct_change >= 0:
        return "➡️ Stable (Slight growth)"
    elif pct_change >= -10:
        return "⚠️ Declining (-0 to -10%)"
    elif pct_change >= -20:
        return "🟡 Significant Decline (-10 to -20%)"
    else:
        return "🔴 Severe Decline (>-20%)"


def _rate_transaction_velocity(monthly_volume: float, pct_change: float) -> str:
    """Rate transaction velocity."""
    if monthly_volume >= 10000 and pct_change >= 10:
        return "Very High (Strong activity + growth)"
    elif monthly_volume >= 5000 and pct_change >= 0:
        return "High (Good activity + stable/growing)"
    elif monthly_volume >= 2000:
        return "Medium (Moderate activity)"
    elif monthly_volume >= 500:
        return "Low (Limited activity)"
    else:
        return "Very Low (Minimal activity)"


def _calculate_payment_health_score(late_payments: int, avg_days_late: int, dpo: int) -> float:
    """Calculate payment health score (0-100, higher = worse)."""
    score = 10  # Base score
    
    # Late payments
    if late_payments >= 15:
        score += 60
    elif late_payments >= 10:
        score += 45
    elif late_payments >= 5:
        score += 30
    elif late_payments >= 3:
        score += 15
    elif late_payments >= 1:
        score += 5
    
    # Average days late
    if avg_days_late >= 45:
        score += 40
    elif avg_days_late >= 30:
        score += 30
    elif avg_days_late >= 15:
        score += 20
    elif avg_days_late >= 7:
        score += 10
    
    # Days payable outstanding
    if dpo >= 120:
        score += 25
    elif dpo >= 90:
        score += 15
    elif dpo >= 75:
        score += 8
    
    return min(score, 100)


def _rate_payment_health(score: float) -> str:
    """Rate payment health."""
    if score < 20:
        return "Excellent (Minimal Risk)"
    elif score < 35:
        return "Good (Low Risk)"
    elif score < 55:
        return "Fair (Medium Risk)"
    elif score < 75:
        return "Poor (High Risk)"
    else:
        return "Critical (Very High Risk)"


def _identify_payment_concerns(late_payments: int, avg_days_late: int, dpo: int) -> list:
    """Identify payment concerns."""
    concerns = []
    
    if late_payments >= 10:
        concerns.append(f"Chronic late payment pattern ({late_payments} in 6 months)")
    elif late_payments >= 5:
        concerns.append(f"Frequent late payments ({late_payments} in 6 months)")
    elif late_payments >= 3:
        concerns.append(f"Multiple late payments ({late_payments} in 6 months)")
    
    if avg_days_late >= 30:
        concerns.append(f"Severely delayed payments (avg {avg_days_late} days late)")
    elif avg_days_late >= 15:
        concerns.append(f"Significantly late payments (avg {avg_days_late} days late)")
    
    if dpo >= 120:
        concerns.append(f"Extremely extended payment terms ({dpo} days)")
    elif dpo >= 90:
        concerns.append(f"Very long payment terms ({dpo} days)")
    
    return concerns


def _payment_risk_points(health_score: float) -> str:
    """Map payment health to risk points."""
    if health_score < 25:
        return "5-10"
    elif health_score < 45:
        return "10-25"
    elif health_score < 65:
        return "25-45"
    else:
        return "45-70"


def _interpret_payment_stress(severity: str, late_payments: int, avg_days_late: int) -> str:
    """Interpret payment stress level."""
    if severity == "CRITICAL":
        return "🔴 CRITICAL: Severe payment stress indicates liquidity crisis or financial distress"
    elif severity == "HIGH":
        return "🟠 HIGH RISK: Significant payment difficulties suggest cash flow problems"
    elif severity == "MEDIUM":
        return "🟡 MODERATE: Some payment delays may indicate temporary cash constraints"
    elif severity == "LOW":
        return "⚠️ WATCH: Minor payment issues to monitor"
    else:
        return "✅ HEALTHY: Good payment discipline maintained"


if __name__ == "__main__":
    # Use streamable-http for Cloud Run deployment
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8005))
    )