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
    "timestamp": "2025-11-12T11:00:00Z",
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


# Seeded historic alerts — shown on first load of the Alerts tab.
# Signals use { source, detail } to match the unified Alert type.
HISTORIC_ALERTS: List[Dict[str, Any]] = [
    TECHSTART_ALERT,
    {
        "id": "alert_retail_001",
        "sme_id": "2341",
        "sme_name": "BrightThreads Retail",
        "timestamp": "2025-10-28T09:00:00Z",
        "severity": "warning",
        "title": "Sector Headwinds — Retail Fashion Q3 Downturn",
        "summary": (
            "BrightThreads Retail showing early stress indicators as UK retail "
            "fashion sector contracts 8% QoQ. Inventory turnover slowing and "
            "margins compressing. Risk score moved from 38 to 51."
        ),
        "exposure": 1_200_000,
        "signals": [
            {
                "source": "Sector Data",
                "detail": "UK fashion retail sector revenue down 8% QoQ — worst quarter since 2020.",
            },
            {
                "source": "Payment Data",
                "detail": "Days payable outstanding increased from 42 to 61 days over 90-day window.",
            },
        ],
        "recommendation": (
            "Monitor inventory financing covenant. Request Q3 management accounts "
            "ahead of scheduled annual review."
        ),
    },
    {
        "id": "alert_construction_001",
        "sme_id": "1892",
        "sme_name": "Apex Construction Group",
        "timestamp": "2025-10-15T14:20:00Z",
        "severity": "warning",
        "title": "Interest Rate Sensitivity — Refinancing Risk Elevated",
        "summary": (
            "Apex Construction Group's variable-rate facilities now represent 74% "
            "of total debt following recent drawdown. With base rate at 5.25%, "
            "debt service coverage ratio has fallen to 1.18x — approaching 1.1x covenant."
        ),
        "exposure": 3_400_000,
        "signals": [
            {
                "source": "Financial Model",
                "detail": "DSCR dropped from 1.42x to 1.18x following rate increases — covenant trigger at 1.1x.",
            },
            {
                "source": "Companies House",
                "detail": "Latest filed accounts show 22% increase in finance costs YoY.",
            },
        ],
        "recommendation": (
            "Discuss hedging options with client. Flag for watchlist — "
            "next rate decision may breach covenant."
        ),
    },
    {
        "id": "alert_food_001",
        "sme_id": "3105",
        "sme_name": "Harvest Kitchen Ltd",
        "timestamp": "2025-09-30T10:45:00Z",
        "severity": "critical",
        "title": "Regulatory Risk — Allergen Labelling Compliance Failure",
        "summary": (
            "Food Standards Agency issued formal improvement notice to Harvest Kitchen "
            "following allergen labelling audit. Operations suspended at two sites pending "
            "compliance review. Risk score escalated from 52 to 71."
        ),
        "exposure": 890_000,
        "signals": [
            {
                "source": "Regulatory Feed",
                "detail": "FSA improvement notice issued 28 Sep. Two sites suspended — represents 40% of revenue.",
            },
            {
                "source": "Web Analytics",
                "detail": "Google reviews dropped from 4.2 to 3.1 stars over 14 days following press coverage.",
            },
        ],
        "recommendation": (
            "Immediate review call with director. Assess insurance coverage for regulatory action. "
            "Consider facility restructure pending outcome of FSA compliance review."
        ),
    },
]


class AlertService:
    """Service for alert simulation and retrieval."""

    def __init__(self):
        # In-memory store — simulate() appends here so history grows during demo
        self._fired: List[Dict[str, Any]] = []

    async def simulate_alert(self) -> Dict[str, Any]:
        """
        Simulate the TechStart Solutions multi-signal alert.
        Called by POST /api/v1/alerts/simulate — the 'fire the demo' button.
        Returns the pre-crafted alert with a fresh timestamp and stores it.
        """
        alert = dict(TECHSTART_ALERT)
        alert["id"] = f"alert_techstart_{int(datetime.now().timestamp())}"
        alert["timestamp"] = datetime.now().isoformat() + "Z"
        self._fired.append(alert)
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

    async def get_alert_history(
        self,
        sme_id: str = None,
        severity: str = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Return historic alerts — seeded POC data plus any simulate() calls
        made during the current session. Newest first.
        """
        all_alerts = HISTORIC_ALERTS + self._fired

        if sme_id:
            all_alerts = [a for a in all_alerts if a.get("sme_id") == sme_id]
        if severity:
            all_alerts = [a for a in all_alerts if a.get("severity") == severity]

        # Sort newest first, deduplicate by id
        seen = set()
        unique = []
        for a in sorted(all_alerts, key=lambda x: x.get("timestamp", ""), reverse=True):
            if a["id"] not in seen:
                seen.add(a["id"])
                unique.append(a)

        return {
            "alerts": unique[:limit],
            "count": len(unique),
        }


_alert_service = None

def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service