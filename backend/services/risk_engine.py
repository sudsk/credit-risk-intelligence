"""
Risk Engine Service
Implements the credit risk calculation methodology from CREDIT_RISK_METHODOLOGY.md
"""

import math
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# ── Rating / PD helpers ────────────────────────────────────────────────────

# Ordered from lowest risk to highest — used for notch-gap calculation
RATING_NOTCHES: List[str] = [
    "AAA", "AA+", "AA", "AA-",
    "A+",  "A",   "A-",
    "BBB+","BBB", "BBB-",
    "BB+", "BB",  "BB-",
    "B+",  "B",   "B-",
    "CCC", "CC",  "C",   "D",
]

# Sentiment signal impact weights (score points added to risk score)
# Positive = increases risk score (bad).  Used in score delta narrative.
SIGNAL_WEIGHTS: Dict[str, int] = {
    # Executive / people signals
    "ceo_departure":         12,
    "cfo_departure":         12,
    "cto_departure":         12,
    "c_level_departure":     10,
    "director_change":        6,
    # Financial signals
    "payment_delays":         8,
    "covenant_breach":        9,
    "cash_reserves_decline":  5,
    "revenue_decline":        6,
    "ebitda_compression":     4,
    # Market / external signals
    "web_traffic_drop_40":    8,   # >40% drop
    "web_traffic_drop_25":    5,   # 25-40% drop
    "sector_headwinds":       4,
    "regulatory_review":      7,
    # Positive signals (reduce risk score)
    "strong_trading":        -3,
    "cash_improvement":      -2,
    "sector_recovery":       -1,
    # Misc
    "bad_press":              3,
    "esg_issue":              6,
    "insolvency_flag":       15,
}

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "mcp-servers" / "data"
SMES_CSV = DATA_DIR / "smes.csv"

# Load SME data once at module level
smes_df = pd.read_csv(SMES_CSV)


class RiskEngine:
    """
    Credit Risk Calculation Engine

    Calculates composite risk scores and default probabilities using:
    - Financial Score       (40%)
    - Operational Score     (25%)
    - Market Score          (20%)
    - Alternative Data Score(15%)
    """

    # Sector risk coefficients for PD calculation
    SECTOR_BETA = {
        "Construction":         0.8,
        "Retail/Fashion":       0.6,
        "Food/Hospitality":     0.5,
        "Manufacturing":        0.2,
        "Software/Technology": -0.3,
        "Healthcare":          -0.4,
        "Energy/Utilities":    -0.2,
        "Marketing Services":   0.3,
        "Professional Services":-0.1,
        "Logistics":            0.1,
    }

    # Base sector risk scores
    SECTOR_BASE_RISK = {
        "Software/Technology":  25,
        "Healthcare":           20,
        "Energy/Utilities":     30,
        "Manufacturing":        35,
        "Retail/Fashion":       55,
        "Food/Hospitality":     50,
        "Construction":         60,
        "Marketing Services":   45,
        "Professional Services":30,
        "Logistics":            40,
    }

    def __init__(self):
        self.mcp_clients = {}

        # Load alternative data CSVs once — reused across all SME calculations
        self._departures_df = pd.read_csv(DATA_DIR / "departures.csv")
        self._employees_df  = pd.read_csv(DATA_DIR / "employees.csv")
        self._traffic_df    = pd.read_csv(DATA_DIR / "web_traffic.csv")
        self._news_df       = pd.read_csv(DATA_DIR / "news_events.csv")
        self._companies_df  = pd.read_csv(DATA_DIR / "company_info.csv")

        logger.info("RiskEngine initialised — alternative data CSVs loaded")

    async def register_mcp_client(self, name: str, client):
        """Register an MCP client for data retrieval."""
        self.mcp_clients[name] = client

    async def calculate_risk_score(self, sme_id: str) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an SME.

        Returns:
            Dict containing risk_score, risk_category, default_probability,
            and component breakdowns.
        """
        sme_row = smes_df[smes_df['id'] == sme_id]
        if sme_row.empty:
            raise ValueError(f"SME {sme_id} not found")

        sme = sme_row.iloc[0]

        financial_score    = await self._calc_financial_score(sme_id, sme)
        operational_score  = await self._calc_operational_score(sme_id, sme)
        market_score       = await self._calc_market_score(sme_id, sme)
        alt_data_score     = await self._calc_alternative_data_score(sme_id, sme)

        risk_score = (
            financial_score   * 0.40 +
            operational_score * 0.25 +
            market_score      * 0.20 +
            alt_data_score    * 0.15
        )

        risk_score    = round(max(0, min(100, risk_score)))
        risk_category = self._get_risk_category(risk_score)
        pd_12m        = self._calc_default_probability(risk_score, sme)

        # ── Rating & PD overlay fields (from enriched CSV) ─────────────────
        indicative_grade = self.score_to_indicative_grade(risk_score)
        bank_rating      = str(sme.get('bank_rating', 'BBB'))
        gap_notches      = self.rating_gap_notches(indicative_grade, bank_rating)
        pd_original      = float(sme.get('pd_original', round(pd_12m * 100, 1)))
        pd_adjusted      = float(sme.get('pd_adjusted', round(pd_12m * 100, 1)))
        score_previous   = int(sme.get('score_previous', risk_score))

        # ── Score delta narrative ───────────────────────────────────────────
        active_signals   = self._get_active_signals_for_sme(sme_id, sme)
        score_narrative  = self._build_score_delta_narrative(
            sme_id, risk_score, score_previous, active_signals
        )

        return {
            "sme_id":                  sme_id,
            "sme_name":                sme['name'],
            "risk_score":              risk_score,
            "risk_category":           risk_category,
            "default_probability_12m": round(pd_12m, 3),
            "components": {
                "financial":        round(financial_score, 1),
                "operational":      round(operational_score, 1),
                "market":           round(market_score, 1),
                "alternative_data": round(alt_data_score, 1),
            },
            # Rating overlay — live score vs bank's static rating
            "indicative_grade":   indicative_grade,
            "bank_rating":        bank_rating,
            "rating_gap_notches": gap_notches,
            # PD overlay — bank's static PD vs our signal-adjusted PD
            "pd_original":        pd_original,   # bank's system PD (%)
            "pd_adjusted":        pd_adjusted,   # our overlay PD (%)
            # Score delta narrative
            "score_previous":     score_previous,
            "score_narrative":    score_narrative,
            "active_signals":     [
                {"label": label, "impact": pts}
                for label, pts in active_signals[:5]
            ],
            # Standard fields
            "exposure":           float(sme['exposure']),
            "sector":             sme['sector'],
            "geography":          sme['geography'],
            # Detail panel fields
            "bank_rating_stale":  gap_notches >= 2,  # flag for UI warning banner
            "sector_health":      str(sme.get('sector_health', 'stable')),
            "geography_risk":     str(sme.get('geography_risk', 'low')),
            "compliance_status":  str(sme.get('compliance_status', 'compliant')),
            "net_profit_margin":  float(sme.get('net_profit_margin', 0)),
            "loan_origination_date": str(sme.get('loan_origination_date', '')),
        }

    # ------------------------------------------------------------------
    # Component calculators
    # ------------------------------------------------------------------

    async def _calc_financial_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Financial Score (40% of total)

        Sub-components:
        - DSCR          (30%)
        - Current Ratio (25%)
        - Debt/Equity   (20%)
        - Cash Runway   (15%)
        - EBITDA Margin (10%)
        """
        dscr           = float(sme['debt_service_coverage'])
        current_ratio  = float(sme['current_ratio'])
        debt_to_equity = float(sme['debt']) / max(float(sme['revenue']) - float(sme['debt']), 1)

        monthly_revenue  = float(sme['revenue']) / 12
        monthly_expenses = monthly_revenue * 0.85  # assume 15% margin
        cash_runway      = float(sme['cash_reserves']) / monthly_expenses if monthly_expenses > 0 else 12

        ebitda_margin = (
            float(sme['ebitda']) / float(sme['revenue']) * 100
            if float(sme['revenue']) > 0 else 0
        )

        return (
            self._score_dscr(dscr)                     * 0.30 +
            self._score_current_ratio(current_ratio)   * 0.25 +
            self._score_debt_to_equity(debt_to_equity) * 0.20 +
            self._score_cash_runway(cash_runway)       * 0.15 +
            self._score_ebitda_margin(ebitda_margin)   * 0.10
        )

    async def _calc_operational_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Operational Score (25% of total)

        Sub-components:
        - Revenue Growth YoY  (40%)
        - Revenue Trend QoQ   (30%)
        - Payment Days Trend  (30%)
        """
        revenue_growth = float(sme.get('trend_value', 0))
        payment_days   = 35 if sme.get('trend', 'stable') == 'stable' else 47
        payment_trend  = "increasing" if sme.get('trend', 'stable') == 'down' else "stable"

        return (
            self._score_revenue_growth(revenue_growth)          * 0.40 +
            self._score_revenue_trend(revenue_growth)           * 0.30 +
            self._score_payment_days(payment_days, payment_trend) * 0.30
        )

    async def _calc_market_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Market Score (20% of total)

        Sub-components:
        - Sector Risk          (40%)
        - Competitive Position (30%)
        - Geographic Risk      (30%)
        """
        sector    = sme['sector']
        geography = sme['geography']
        revenue   = float(sme['revenue'])

        sector_score = self.SECTOR_BASE_RISK.get(sector, 40)

        if revenue > 5_000_000:
            competitive_score = 15
        elif revenue > 3_000_000:
            competitive_score = 30
        elif revenue > 1_500_000:
            competitive_score = 50
        else:
            competitive_score = 75

        if geography == "UK":
            geo_score = 15 if sme.get('trend', 'stable') == 'up' else 20
        elif geography == "EU":
            geo_score = 30
        else:
            geo_score = 40

        return (
            sector_score      * 0.40 +
            competitive_score * 0.30 +
            geo_score         * 0.30
        )

    async def _calc_alternative_data_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Alternative Data Score (15% of total)

        Sub-components:
        - Employee Signals      (35%)
        - Web Traffic Signals   (30%)
        - News Sentiment        (20%)
        - Companies House Flags (15%)
        """
        sme_id_str = str(sme_id)

        # 1. EMPLOYEE SIGNALS (35%)
        try:
            departures = self._departures_df[
                self._departures_df['sme_id'].astype(str) == sme_id_str
            ]
            emp_data = self._employees_df[
                self._employees_df['sme_id'].astype(str) == sme_id_str
            ]

            c_level_departures = len(departures[departures['seniority'] == 'C-Level'])
            emp_trend = emp_data.iloc[0]['trend'] if not emp_data.empty else 'stable'

            if c_level_departures >= 2:   employee_score = 85
            elif c_level_departures == 1: employee_score = 70
            elif emp_trend == 'down':     employee_score = 55
            elif emp_trend == 'up':       employee_score = 15
            else:                         employee_score = 30
        except Exception as e:
            logger.warning(f"Employee signal calc failed for {sme_id}: {e}")
            employee_score = 30

        # 2. WEB TRAFFIC SIGNALS (30%)
        try:
            traffic_data = self._traffic_df[
                self._traffic_df['sme_id'].astype(str) == sme_id_str
            ]

            if not traffic_data.empty:
                traffic_change = float(traffic_data.iloc[0]['users_change_qoq'])

                if traffic_change < -40:   traffic_score = 95
                elif traffic_change < -25: traffic_score = 75
                elif traffic_change < -10: traffic_score = 50
                elif traffic_change > 10:  traffic_score = 15
                else:                      traffic_score = 30
            else:
                traffic_score = 50
        except Exception as e:
            logger.warning(f"Web traffic signal calc failed for {sme_id}: {e}")
            traffic_score = 50

        # 3. NEWS SENTIMENT (20%)
        try:
            news_data = self._news_df[
                self._news_df['sme_id'].astype(str) == sme_id_str
            ]

            if not news_data.empty:
                critical_events = len(news_data[news_data['severity'] == 'critical'])
                avg_sentiment   = float(news_data['sentiment_score'].mean())

                if critical_events >= 2 or avg_sentiment < -0.7:   news_score = 95
                elif critical_events == 1 or avg_sentiment < -0.4: news_score = 70
                elif avg_sentiment > 0.5:                           news_score = 15
                else:                                               news_score = 30
            else:
                news_score = 30
        except Exception as e:
            logger.warning(f"News sentiment calc failed for {sme_id}: {e}")
            news_score = 30

        # 4. COMPANIES HOUSE FLAGS (15%)
        try:
            company_data = self._companies_df[
                self._companies_df['sme_id'].astype(str) == sme_id_str
            ]

            if not company_data.empty:
                row              = company_data.iloc[0]
                director_changes = int(row['director_changes_12m'])
                ccj_count        = int(row['ccj_count'])
                insolvency       = bool(row['insolvency_flag'])

                if insolvency:                                    companies_house_score = 95
                elif ccj_count >= 3 or director_changes >= 3:    companies_house_score = 80
                elif ccj_count >= 1 or director_changes >= 2:    companies_house_score = 50
                else:                                             companies_house_score = 20
            else:
                companies_house_score = 30
        except Exception as e:
            logger.warning(f"Companies House calc failed for {sme_id}: {e}")
            companies_house_score = 30

        return (
            employee_score        * 0.35 +
            traffic_score         * 0.30 +
            news_score            * 0.20 +
            companies_house_score * 0.15
        )

    # ------------------------------------------------------------------
    # Rating & PD helpers
    # ------------------------------------------------------------------

    def score_to_indicative_grade(self, score: int) -> str:
        """
        Map 0-100 risk score to indicative credit notation.
        Higher score = higher risk = lower grade.
        This is our live overlay grade — NOT the bank's official rating.
        """
        if score <= 20:  return "AAA"
        elif score <= 28: return "AA"
        elif score <= 35: return "A"
        elif score <= 42: return "BBB+"
        elif score <= 50: return "BBB"
        elif score <= 57: return "BB+"
        elif score <= 63: return "BB"
        elif score <= 70: return "B"
        elif score <= 78: return "CCC"
        elif score <= 88: return "CC"
        else:             return "C"

    def rating_gap_notches(self, indicative_grade: str, bank_rating: str) -> int:
        """
        Calculate how many notches our indicative grade is below the bank's
        official rating.  Positive = we see MORE risk than the bank's model.
        e.g. bank says BB+, we say B → gap = 3 notches (flag as stale)
        """
        try:
            our_idx  = RATING_NOTCHES.index(indicative_grade)
            bank_idx = RATING_NOTCHES.index(bank_rating)
            return our_idx - bank_idx   # positive = we rate worse than bank
        except ValueError:
            logger.warning(
                f"Unknown rating in gap calc: indicative={indicative_grade} bank={bank_rating}"
            )
            return 0

    def _build_score_delta_narrative(
        self,
        sme_id: str,
        score_current: int,
        score_previous: int,
        active_signals: List[Tuple[str, int]],
    ) -> str:
        """
        Build a standardised score delta narrative for the UI.

        Format: "Score moved {prev}→{curr} because: (1) Signal A +Xpts, (2) ..."
        If score hasn't changed materially, returns a stable narrative.

        active_signals: list of (signal_label, point_impact) sorted by abs impact desc
        """
        delta = score_current - score_previous
        if abs(delta) < 2 or not active_signals:
            return f"Score stable at {score_current} — no significant signal changes in review period"

        direction = "↑" if delta > 0 else "↓"
        parts = []
        for i, (label, pts) in enumerate(active_signals[:3], start=1):
            sign = "+" if pts > 0 else ""
            parts.append(f"({i}) {label} {sign}{pts}pts")

        return (
            f"Score moved {score_previous}→{score_current} {direction}{abs(delta)}pts because: "
            + ", ".join(parts)
        )

    def _get_active_signals_for_sme(
        self, sme_id: str, sme: pd.Series
    ) -> List[Tuple[str, int]]:
        """
        Derive which signals are active for this SME based on alt data CSVs.
        Returns list of (human-readable label, score impact) sorted by abs impact desc.
        Used to build the score delta narrative.
        """
        sme_id_str = str(sme_id)
        signals: List[Tuple[str, int]] = []

        try:
            departures = self._departures_df[
                self._departures_df['sme_id'].astype(str) == sme_id_str
            ]
            for _, dep in departures.iterrows():
                role = str(dep.get('role', '')).upper()
                name = str(dep.get('name', 'Executive'))
                if 'CEO' in role:
                    signals.append((f"CEO departure ({name})", SIGNAL_WEIGHTS["ceo_departure"]))
                elif 'CFO' in role:
                    signals.append((f"CFO departure ({name})", SIGNAL_WEIGHTS["cfo_departure"]))
                elif 'CTO' in role:
                    signals.append((f"CTO departure ({name})", SIGNAL_WEIGHTS["cto_departure"]))
                elif dep.get('seniority') == 'C-Level':
                    signals.append((f"C-level departure ({name})", SIGNAL_WEIGHTS["c_level_departure"]))
                else:
                    signals.append((f"Director change ({name})", SIGNAL_WEIGHTS["director_change"]))
        except Exception as e:
            logger.warning(f"Signal derivation (departures) failed for {sme_id}: {e}")

        try:
            traffic_data = self._traffic_df[
                self._traffic_df['sme_id'].astype(str) == sme_id_str
            ]
            if not traffic_data.empty:
                change = float(traffic_data.iloc[0]['users_change_qoq'])
                if change < -40:
                    signals.append((f"Web traffic {change:.0f}% QoQ", SIGNAL_WEIGHTS["web_traffic_drop_40"]))
                elif change < -25:
                    signals.append((f"Web traffic {change:.0f}% QoQ", SIGNAL_WEIGHTS["web_traffic_drop_25"]))
                elif change > 10:
                    signals.append((f"Web traffic +{change:.0f}% QoQ", SIGNAL_WEIGHTS["strong_trading"]))
        except Exception as e:
            logger.warning(f"Signal derivation (traffic) failed for {sme_id}: {e}")

        try:
            news_data = self._news_df[
                self._news_df['sme_id'].astype(str) == sme_id_str
            ]
            if not news_data.empty:
                critical = news_data[news_data['severity'] == 'critical']
                for _, article in critical.iterrows():
                    headline = str(article.get('headline', 'Critical event'))[:50]
                    signals.append((headline, SIGNAL_WEIGHTS["bad_press"]))
        except Exception as e:
            logger.warning(f"Signal derivation (news) failed for {sme_id}: {e}")

        try:
            company_data = self._companies_df[
                self._companies_df['sme_id'].astype(str) == sme_id_str
            ]
            if not company_data.empty:
                row = company_data.iloc[0]
                if bool(row.get('insolvency_flag', False)):
                    signals.append(("Insolvency flag raised", SIGNAL_WEIGHTS["insolvency_flag"]))
                ccj = int(row.get('ccj_count', 0))
                if ccj > 0:
                    signals.append((f"{ccj} CCJ(s) registered", SIGNAL_WEIGHTS["payment_delays"]))
        except Exception as e:
            logger.warning(f"Signal derivation (companies house) failed for {sme_id}: {e}")

        # Sort by absolute impact descending — biggest movers first
        signals.sort(key=lambda x: abs(x[1]), reverse=True)
        return signals

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _score_dscr(self, dscr: float) -> float:
        if dscr > 2.5:   return 5
        elif dscr > 2.0: return 15
        elif dscr > 1.5: return 30
        elif dscr > 1.2: return 50
        elif dscr > 1.0: return 70
        else:            return 95

    def _score_current_ratio(self, ratio: float) -> float:
        if ratio > 2.0:   return 5
        elif ratio > 1.5: return 15
        elif ratio > 1.2: return 35
        elif ratio > 1.0: return 60
        else:             return 90

    def _score_debt_to_equity(self, de_ratio: float) -> float:
        if de_ratio < 0.5:   return 5
        elif de_ratio < 1.0: return 15
        elif de_ratio < 1.5: return 30
        elif de_ratio < 2.0: return 50
        elif de_ratio < 3.0: return 75
        else:                return 95

    def _score_cash_runway(self, months: float) -> float:
        if months > 12:   return 5
        elif months > 9:  return 20
        elif months > 6:  return 40
        elif months > 3:  return 70
        else:             return 95

    def _score_ebitda_margin(self, margin: float) -> float:
        if margin > 25:   return 5
        elif margin > 20: return 15
        elif margin > 15: return 25
        elif margin > 10: return 40
        elif margin > 5:  return 65
        else:             return 90

    def _score_revenue_growth(self, growth: float) -> float:
        if growth > 20:   return 10
        elif growth > 10: return 20
        elif growth > 5:  return 30
        elif growth > 0:  return 45
        elif growth > -5: return 70
        else:             return 95

    def _score_revenue_trend(self, qoq_growth: float) -> float:
        if qoq_growth > 5:    return 10
        elif qoq_growth > 0:  return 25
        elif qoq_growth > -2: return 40
        elif qoq_growth > -5: return 65
        else:                 return 90

    def _score_payment_days(self, days: int, trend: str) -> float:
        if trend == "decreasing":            return 10
        elif days < 30:                      return 25
        elif days < 45:                      return 50
        elif trend == "increasing" and days > 45: return 75
        else:                                return 95

    def _get_risk_category(self, risk_score: int) -> str:
        if risk_score < 35:   return "stable"
        elif risk_score < 60: return "medium"
        else:                 return "critical"

    def _calc_default_probability(self, risk_score: int, sme: pd.Series) -> float:
        """
        12-month PD via logistic regression:
        PD = 1 / (1 + e^(-z))
        z  = β0 + β1(Risk_Score) + β2(Sector) + β3(Size)
        """
        sector  = sme['sector']
        revenue = float(sme['revenue'])

        beta_2 = self.SECTOR_BETA.get(sector, 0)
        beta_3 = -1.0 if revenue < 1_000_000 else (-0.5 if revenue < 3_000_000 else (0 if revenue < 5_000_000 else 0.5))

        z       = -5.2 + (0.12 * risk_score) + beta_2 + beta_3
        pd_base = 1 / (1 + math.exp(-z))

        risk_category = sme.get('risk_category', 'medium')
        multiplier    = 1.4 if risk_category == 'critical' else (1.1 if risk_category == 'medium' else 0.9)

        return min(pd_base * multiplier, 0.95)

    async def batch_calculate_risk_scores(self, sme_ids: list) -> list:
        """Calculate risk scores for multiple SMEs."""
        results = []
        for sme_id in sme_ids:
            try:
                results.append(await self.calculate_risk_score(sme_id))
            except Exception as e:
                results.append({"sme_id": sme_id, "error": str(e)})
        return results


# Singleton
_risk_engine = None

def get_risk_engine() -> RiskEngine:
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine