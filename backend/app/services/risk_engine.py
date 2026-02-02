"""
Risk Engine Service
Implements the credit risk calculation methodology from CREDIT_RISK_METHODOLOGY.md
"""

import math
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import asyncio

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SMES_CSV = DATA_DIR / "smes.csv"

# Load SME data
smes_df = pd.read_csv(SMES_CSV)

class RiskEngine:
    """
    Credit Risk Calculation Engine
    
    Calculates composite risk scores and default probabilities using:
    - Financial Score (40%)
    - Operational Score (25%)
    - Market Score (20%)
    - Alternative Data Score (15%)
    """
    
    # Sector risk coefficients for PD calculation
    SECTOR_BETA = {
        "Construction": 0.8,
        "Retail/Fashion": 0.6,
        "Food/Hospitality": 0.5,
        "Manufacturing": 0.2,
        "Software/Technology": -0.3,
        "Healthcare": -0.4,
        "Energy/Utilities": -0.2,
        "Marketing Services": 0.3,
        "Professional Services": -0.1,
        "Logistics": 0.1
    }
    
    # Base sector risk scores
    SECTOR_BASE_RISK = {
        "Software/Technology": 25,
        "Healthcare": 20,
        "Energy/Utilities": 30,
        "Manufacturing": 35,
        "Retail/Fashion": 55,
        "Food/Hospitality": 50,
        "Construction": 60,
        "Marketing Services": 45,
        "Professional Services": 30,
        "Logistics": 40
    }
    
    def __init__(self):
        self.mcp_clients = {}
    
    async def register_mcp_client(self, name: str, client):
        """Register an MCP client for data retrieval."""
        self.mcp_clients[name] = client
    
    async def calculate_risk_score(self, sme_id: str) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an SME.
        
        Returns:
            Dict containing risk_score, risk_category, default_probability, and component breakdowns
        """
        # Get SME base data
        sme_row = smes_df[smes_df['id'] == sme_id]
        if sme_row.empty:
            raise ValueError(f"SME {sme_id} not found")
        
        sme = sme_row.iloc[0]
        
        # Calculate component scores
        financial_score = await self._calc_financial_score(sme_id, sme)
        operational_score = await self._calc_operational_score(sme_id, sme)
        market_score = await self._calc_market_score(sme_id, sme)
        alt_data_score = await self._calc_alternative_data_score(sme_id, sme)
        
        # Weighted composite
        risk_score = (
            financial_score * 0.40 +
            operational_score * 0.25 +
            market_score * 0.20 +
            alt_data_score * 0.15
        )
        
        # Round and constrain
        risk_score = round(max(0, min(100, risk_score)))
        
        # Determine risk category
        risk_category = self._get_risk_category(risk_score)
        
        # Calculate default probability
        pd_12m = self._calc_default_probability(risk_score, sme)
        
        return {
            "sme_id": sme_id,
            "sme_name": sme['name'],
            "risk_score": risk_score,
            "risk_category": risk_category,
            "default_probability_12m": round(pd_12m, 3),
            "components": {
                "financial": round(financial_score, 1),
                "operational": round(operational_score, 1),
                "market": round(market_score, 1),
                "alternative_data": round(alt_data_score, 1)
            },
            "exposure": float(sme['exposure']),
            "sector": sme['sector'],
            "geography": sme['geography']
        }
    
    async def _calc_financial_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Calculate Financial Score (40% of total)
        
        Sub-components:
        - DSCR (30%)
        - Current Ratio (25%)
        - Debt-to-Equity (20%)
        - Cash Runway (15%)
        - EBITDA Margin (10%)
        """
        # Get financial data from CSV (in real impl, from MCP server)
        dscr = float(sme['debt_service_coverage'])
        current_ratio = float(sme['current_ratio'])
        debt_to_equity = float(sme['debt']) / max(float(sme['revenue']) - float(sme['debt']), 1)
        
        # Calculate cash runway
        monthly_revenue = float(sme['revenue']) / 12
        monthly_expenses = monthly_revenue * (1 - 0.15)  # Assuming 15% margin
        cash_runway = float(sme['cash_reserves']) / monthly_expenses if monthly_expenses > 0 else 12
        
        ebitda_margin = float(sme['ebitda']) / float(sme['revenue']) * 100 if float(sme['revenue']) > 0 else 0
        
        # Score each component
        dscr_score = self._score_dscr(dscr)
        current_ratio_score = self._score_current_ratio(current_ratio)
        de_score = self._score_debt_to_equity(debt_to_equity)
        runway_score = self._score_cash_runway(cash_runway)
        margin_score = self._score_ebitda_margin(ebitda_margin)
        
        # Weighted average
        financial_score = (
            dscr_score * 0.30 +
            current_ratio_score * 0.25 +
            de_score * 0.20 +
            runway_score * 0.15 +
            margin_score * 0.10
        )
        
        return financial_score
    
    async def _calc_operational_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Calculate Operational Score (25% of total)
        
        Sub-components:
        - Revenue Growth YoY (40%)
        - Revenue Trend QoQ (30%)
        - Payment Days Trend (30%)
        """
        # Revenue growth (from trend_value in CSV)
        revenue_growth = float(sme.get('trend_value', 0))
        
        # Payment days - estimate from working capital
        # In real impl, would come from payment_data MCP server
        payment_days = 35 if sme.get('trend', 'stable') == 'stable' else 47
        payment_trend = "increasing" if sme.get('trend', 'stable') == 'down' else "stable"
        
        # Score components
        growth_score = self._score_revenue_growth(revenue_growth)
        trend_score = self._score_revenue_trend(revenue_growth)
        payment_score = self._score_payment_days(payment_days, payment_trend)
        
        operational_score = (
            growth_score * 0.40 +
            trend_score * 0.30 +
            payment_score * 0.30
        )
        
        return operational_score
    
    async def _calc_market_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Calculate Market Score (20% of total)
        
        Sub-components:
        - Sector Risk (40%)
        - Competitive Position (30%)
        - Geographic Risk (30%)
        """
        sector = sme['sector']
        geography = sme['geography']
        revenue = float(sme['revenue'])
        
        # Sector risk
        sector_score = self.SECTOR_BASE_RISK.get(sector, 40)
        
        # Competitive position (based on revenue as proxy)
        if revenue > 5000000:
            competitive_score = 15  # Top quartile
        elif revenue > 3000000:
            competitive_score = 30  # 2nd quartile
        elif revenue > 1500000:
            competitive_score = 50  # 3rd quartile
        else:
            competitive_score = 75  # Bottom quartile
        
        # Geographic risk
        if geography == "UK":
            if sme.get('trend', 'stable') == 'up':
                geo_score = 15
            else:
                geo_score = 20
        elif geography == "EU":
            geo_score = 30
        else:
            geo_score = 40
        
        market_score = (
            sector_score * 0.40 +
            competitive_score * 0.30 +
            geo_score * 0.30
        )
        
        return market_score
    
    async def _calc_alternative_data_score(self, sme_id: str, sme: pd.Series) -> float:
        """
        Calculate Alternative Data Score (15% of total)
        
        Sub-components:
        - Employee Signals (35%)
        - Web Traffic Signals (30%)
        - News Sentiment (20%)
        - Companies House Flags (15%)
        
        This would call MCP servers in production.
        For demo, we use CSV data.
        """
        # Employee signals - use trend from CSV
        employee_trend = sme.get('trend', 'stable')
        if employee_trend == 'down':
            employee_score = 70  # Declining headcount
        elif employee_trend == 'up':
            employee_score = 15  # Hiring
        else:
            employee_score = 30  # Stable
        
        # Web traffic - correlate with risk category
        risk_cat = sme.get('risk_category', 'medium')
        if risk_cat == 'critical':
            traffic_score = 85  # Likely declining traffic
        elif risk_cat == 'medium':
            traffic_score = 45
        else:
            traffic_score = 25
        
        # News sentiment - use risk category as proxy
        if risk_cat == 'critical':
            news_score = 95  # Likely negative news
        elif risk_cat == 'medium':
            news_score = 50
        else:
            news_score = 20
        
        # Companies House - assume compliance for most
        companies_house_score = 30
        
        alt_data_score = (
            employee_score * 0.35 +
            traffic_score * 0.30 +
            news_score * 0.20 +
            companies_house_score * 0.15
        )
        
        return alt_data_score
    
    def _score_dscr(self, dscr: float) -> float:
        """Score Debt Service Coverage Ratio."""
        if dscr > 2.5:
            return 5
        elif dscr > 2.0:
            return 15
        elif dscr > 1.5:
            return 30
        elif dscr > 1.2:
            return 50
        elif dscr > 1.0:
            return 70
        else:
            return 95
    
    def _score_current_ratio(self, ratio: float) -> float:
        """Score Current Ratio."""
        if ratio > 2.0:
            return 5
        elif ratio > 1.5:
            return 15
        elif ratio > 1.2:
            return 35
        elif ratio > 1.0:
            return 60
        else:
            return 90
    
    def _score_debt_to_equity(self, de_ratio: float) -> float:
        """Score Debt-to-Equity Ratio."""
        if de_ratio < 0.5:
            return 5
        elif de_ratio < 1.0:
            return 15
        elif de_ratio < 1.5:
            return 30
        elif de_ratio < 2.0:
            return 50
        elif de_ratio < 3.0:
            return 75
        else:
            return 95
    
    def _score_cash_runway(self, months: float) -> float:
        """Score Cash Runway."""
        if months > 12:
            return 5
        elif months > 9:
            return 20
        elif months > 6:
            return 40
        elif months > 3:
            return 70
        else:
            return 95
    
    def _score_ebitda_margin(self, margin: float) -> float:
        """Score EBITDA Margin."""
        if margin > 25:
            return 5
        elif margin > 20:
            return 15
        elif margin > 15:
            return 25
        elif margin > 10:
            return 40
        elif margin > 5:
            return 65
        else:
            return 90
    
    def _score_revenue_growth(self, growth: float) -> float:
        """Score Revenue Growth YoY."""
        if growth > 20:
            return 10
        elif growth > 10:
            return 20
        elif growth > 5:
            return 30
        elif growth > 0:
            return 45
        elif growth > -5:
            return 70
        else:
            return 95
    
    def _score_revenue_trend(self, qoq_growth: float) -> float:
        """Score Revenue Trend QoQ."""
        if qoq_growth > 5:
            return 10
        elif qoq_growth > 0:
            return 25
        elif qoq_growth > -2:
            return 40
        elif qoq_growth > -5:
            return 65
        else:
            return 90
    
    def _score_payment_days(self, days: int, trend: str) -> float:
        """Score Payment Days."""
        base_score = 0
        
        if trend == "decreasing":
            base_score = 10
        elif days < 30:
            base_score = 25
        elif days < 45:
            base_score = 50
        elif trend == "increasing" and days > 45:
            base_score = 75
        else:
            base_score = 95
        
        return base_score
    
    def _get_risk_category(self, risk_score: int) -> str:
        """Determine risk category from risk score."""
        if risk_score < 35:
            return "stable"
        elif risk_score < 60:
            return "medium"
        else:
            return "critical"
    
    def _calc_default_probability(self, risk_score: int, sme: pd.Series) -> float:
        """
        Calculate 12-month default probability using logistic regression.
        
        PD = 1 / (1 + e^(-z))
        where z = β0 + β1(Risk_Score) + β2(Sector) + β3(Size)
        """
        # Base coefficients
        beta_0 = -5.2
        beta_1 = 0.12
        
        # Sector adjustment
        sector = sme['sector']
        beta_2 = self.SECTOR_BETA.get(sector, 0)
        
        # Size adjustment
        revenue = float(sme['revenue'])
        if revenue < 1000000:
            beta_3 = -1.0
        elif revenue < 3000000:
            beta_3 = -0.5
        elif revenue < 5000000:
            beta_3 = 0
        else:
            beta_3 = 0.5
        
        # Calculate z
        z = beta_0 + (beta_1 * risk_score) + beta_2 + beta_3
        
        # Logistic function
        pd_base = 1 / (1 + math.exp(-z))
        
        # Alternative data multipliers (simplified for demo)
        risk_category = sme.get('risk_category', 'medium')
        
        if risk_category == 'critical':
            pd_adjusted = pd_base * 1.4  # Critical events multiplier
        elif risk_category == 'medium':
            pd_adjusted = pd_base * 1.1
        else:
            pd_adjusted = pd_base * 0.9  # Positive signals
        
        # Cap at 95%
        return min(pd_adjusted, 0.95)
    
    async def batch_calculate_risk_scores(self, sme_ids: list) -> list:
        """Calculate risk scores for multiple SMEs."""
        results = []
        for sme_id in sme_ids:
            try:
                score = await self.calculate_risk_score(sme_id)
                results.append(score)
            except Exception as e:
                results.append({
                    "sme_id": sme_id,
                    "error": str(e)
                })
        return results


# Singleton instance
_risk_engine = None

def get_risk_engine() -> RiskEngine:
    """Get singleton risk engine instance."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine