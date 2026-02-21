"""
Alert Service
Returns pre-crafted demo alerts for the POC.

TechStart Solutions (#4567) is the "aha moment" of the demo:
multi-signal alert combining CTO departure + web traffic drop + payment delays.
"""
from datetime import datetime
from typing import Dict, Any, List


# Pre-crafted demo alert — central to the 5-minute demo path
TECHSTART_ALERT = {
    "id": "alert_techstart_001",
    "sme_id": "4567",
    "sme_name": "TechStart Solutions",
    "generated_at": datetime.now().isoformat() + "Z",
    "severity": "critical",
    "risk_score_before": 45,
    "risk_score_after": 68,
    "risk_score_delta": 23,
    "title": "Multi-Signal Risk Escalation — Immediate Review Required",
    "summary": (
        "Three concurrent adverse signals detected for TechStart Solutions. "
        "Risk score has escalated from 45 (Stable) to 68 (Critical) in 30 days. "
        "Recommend immediate relationship manager review."
    ),
    "signals": [
        {
            "signal_type": "executive_departure",
            "severity": "critical",
            "title": "CTO Departure — Unreplaced",
            "detail": (
                "Chief Technology Officer departed 18 days ago. No replacement hired. "
                "CTO had 4-year tenure and was co-founder of core product. "
                "Two senior engineers departed in the same 30-day window."
            ),
            "risk_contribution": +12,
            "source": "LinkedIn / Companies House",
            "detected_at": "2024-11-08T09:15:00Z",
        },
        {
            "signal_type": "web_traffic_decline",
            "severity": "warning",
            "title": "Web Traffic Down 42% QoQ",
            "detail": (
                "Monthly visitors dropped from 34,500 to 19,900 over 90 days. "
                "Bounce rate increased from 38% to 58%. "
                "Conversion rate fell from 4.8% to 2.3%. "
                "Consistent with product instability or customer confidence loss."
            ),
            "risk_contribution": +7,
            "source": "Web Analytics",
            "detected_at": "2024-11-10T14:30:00Z",
        },
        {
            "signal_type": "payment_stress",
            "severity": "warning",
            "title": "Payment Delays Increasing",
            "detail": (
                "Late payments in last 6 months: 5 (up from 1). "
                "Average days late: 12 (up from 3). "
                "Days payable outstanding extended to 67 days. "
                "Pattern consistent with cash flow pressure."
            ),
            "risk_contribution": +4,
            "source": "Payment Data",
            "detected_at": "2024-11-12T11:00:00Z",
        },
    ],
    "recommended_actions": [
        {
            "priority": 1,
            "action": "Schedule urgent review call with CEO",
            "rationale": "CTO departure unreplaced — understand succession plan and product roadmap impact",
            "owner": "Relationship Manager",
            "deadline": "Within 48 hours",
        },
        {
            "priority": 2,
            "action": "Request updated management accounts",
            "rationale": "Payment pattern change suggests possible cash flow deterioration not yet reflected in last filed accounts",
            "owner": "Credit Analyst",
            "deadline": "Within 5 business days",
        },
        {
            "priority": 3,
            "action": "Review covenant compliance on revolving credit facility",
            "rationale": "Risk score now 68 — approaching covenant trigger at 75",
            "owner": "Credit Risk",
            "deadline": "Within 10 business days",
        },
    ],
    "exposure": 2_850_000,
    "facility_type": "Revolving Credit + Term Loan",
    "relationship_manager": "Sarah Chen",
    "last_reviewed": "2024-09-15",
    "next_review_due": "2025-03-15",
}


class AlertService:
    """Service for alert simulation and retrieval."""

    async def simulate_alert(self) -> Dict[str, Any]:
        """
        Simulate the TechStart Solutions multi-signal alert.
        Called by POST /api/v1/alerts/simulate — the 'fire the demo' button.
        Returns the pre-crafted alert with a fresh timestamp.
        """
        alert = dict(TECHSTART_ALERT)
        alert["generated_at"] = datetime.now().isoformat() + "Z"
        return {
            "alert": alert,
            "message": "Alert generated for TechStart Solutions — multi-signal risk escalation detected",
        }

    async def get_active_alerts(self, limit: int = 10) -> Dict[str, Any]:
        """Return active alerts for the portfolio (POC: just TechStart)."""
        return {
            "alerts": [TECHSTART_ALERT],
            "count": 1,
            "critical_count": 1,
        }


_alert_service = None

def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service