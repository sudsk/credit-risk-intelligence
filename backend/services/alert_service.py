"""
Alert Service
Reads historic alerts from backend/data/alerts.csv.
Simulate Live Feed fires the TechStart alert with a fresh timestamp
and appends it to the in-memory store so it appears in history.
"""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "mcp-servers" / "data" / "alerts.csv"

# Max signals per alert in the CSV (columns: signal_N_source, signal_N_detail)
MAX_SIGNALS = 3


def _parse_signals(row: dict) -> List[Dict[str, str]]:
    signals = []
    for i in range(1, MAX_SIGNALS + 1):
        source = row.get(f"signal_{i}_source", "").strip()
        detail = row.get(f"signal_{i}_detail", "").strip()
        if source and detail:
            signals.append({"source": source, "detail": detail})
    return signals


def _row_to_alert(row: dict) -> Dict[str, Any]:
    return {
        "id":             row["id"].strip(),
        "sme_id":         row.get("sme_id", "").strip(),
        "sme_name":       row.get("sme_name", "").strip(),
        "scope":          row.get("scope", "sme").strip(),       # sme | sector | geography | macro
        "affected_count": int(row.get("affected_count", 1) or 1),
        "timestamp":      row["timestamp"].strip(),
        "severity":       row["severity"].strip(),
        "title":          row["title"].strip(),
        "summary":        row["summary"].strip(),
        "exposure":       int(float(row.get("exposure", 0) or 0)),
        "recommendation": row.get("recommendation", "").strip(),
        "signals":        _parse_signals(row),
        "dismissed":      False,
    }


def _load_from_csv() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        logger.warning(f"alerts.csv not found at {DATA_FILE} — starting with empty history")
        return []
    try:
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            return [_row_to_alert(row) for row in csv.DictReader(f)]
    except Exception as e:
        logger.error(f"Failed to load alerts.csv: {e}")
        return []


class AlertService:
    """Loads historic alerts from CSV; simulate() fires the TechStart demo alert."""

    def __init__(self):
        self._historic: List[Dict[str, Any]] = _load_from_csv()
        self._fired:    List[Dict[str, Any]] = []
        logger.info(f"AlertService: loaded {len(self._historic)} historic alerts from CSV")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def simulate_alert(self) -> Dict[str, Any]:
        """
        Fire the TechStart Solutions demo alert with a fresh timestamp.
        Appended to _fired so it immediately appears in get_alert_history().
        """
        base = next(
            (a for a in self._historic if a["sme_id"] == "4567"),
            self._techstart_fallback(),
        )
        alert = dict(base)
        alert["id"]        = f"alert_techstart_{int(datetime.now().timestamp())}"
        alert["timestamp"] = datetime.now().isoformat() + "Z"
        self._fired.append(alert)

        return {
            "alert":   alert,
            "message": "Alert generated for TechStart Solutions — multi-signal risk escalation detected",
        }

    async def get_active_alerts(self, limit: int = 10) -> Dict[str, Any]:
        """Most recent alerts (active view — for home page toast etc.)."""
        all_alerts = self._sorted_alerts()
        active     = all_alerts[:limit]
        return {
            "alerts":         active,
            "count":          len(active),
            "critical_count": sum(1 for a in active if a["severity"] == "critical"),
        }

    async def get_alert_history(
        self,
        sme_id:   Optional[str] = None,
        severity: Optional[str] = None,
        limit:    int = 50,
    ) -> Dict[str, Any]:
        """
        All alerts — CSV seed data + any simulate() calls this session.
        Newest first, deduplicated by id.
        """
        alerts = self._sorted_alerts()

        if sme_id:
            alerts = [a for a in alerts if a["sme_id"] == sme_id]
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        return {
            "alerts": alerts[:limit],
            "count":  len(alerts),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sorted_alerts(self) -> List[Dict[str, Any]]:
        """Merge historic + fired, deduplicate by id, sort newest first."""
        seen, unique = set(), []
        for alert in self._historic + self._fired:
            if alert["id"] not in seen:
                seen.add(alert["id"])
                unique.append(alert)
        return sorted(unique, key=lambda a: a.get("timestamp", ""), reverse=True)

    def _techstart_fallback(self) -> Dict[str, Any]:
        """Fallback if CSV is missing — keeps the demo working regardless."""
        return {
            "id":             "alert_techstart_fallback",
            "sme_id":         "4567",
            "sme_name":       "TechStart Solutions",
            "timestamp":      datetime.now().isoformat() + "Z",
            "severity":       "critical",
            "title":          "Multi-Signal Risk Escalation — Immediate Review Required",
            "summary":        (
                "Three concurrent adverse signals detected. Risk score escalated "
                "from 45 (Stable) to 68 (Critical) in 30 days."
            ),
            "exposure":       2_850_000,
            "recommendation": (
                "Schedule urgent review call with CEO within 48 hours. "
                "Request updated management accounts."
            ),
            "signals": [
                {"source": "LinkedIn / Companies House", "detail": "CTO departed 18 days ago — unreplaced. Co-founder, 4-year tenure."},
                {"source": "Web Analytics",             "detail": "Monthly visitors −42% QoQ. Bounce rate 38%→58%."},
                {"source": "Payment Data",              "detail": "Late payments: 5 in 6m (up from 1). Avg days late: 3→12."},
            ],
            "dismissed": False,
        }


_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service