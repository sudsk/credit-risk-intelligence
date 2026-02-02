"""
Scenario Service
Runs stress test scenarios and portfolio simulations.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from .portfolio_service import get_portfolio_service
from .risk_engine import get_risk_engine

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SMES_CSV = DATA_DIR / "smes.csv"

class ScenarioService:
    """Service for scenario analysis and stress testing."""
    
    def __init__(self):
        self.portfolio_service = get_portfolio_service()
        self.risk_engine = get_risk_engine()
        self.smes_df = pd.read_csv(SMES_CSV)
    
    async def run_scenario(self, scenario_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a stress test scenario.
        
        Args:
            scenario_type: Type of scenario (interest_rate, sector_shock, recession, regulation)
            parameters: Scenario-specific parameters
        
        Returns:
            Scenario results with impact analysis
        """
        if scenario_type == "interest_rate":
            return await self._simulate_interest_rate_shock(parameters)
        elif scenario_type == "sector_shock":
            return await self._simulate_sector_shock(parameters)
        elif scenario_type == "recession":
            return await self._simulate_recession(parameters)
        elif scenario_type == "regulation":
            return await self._simulate_regulation_change(parameters)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    async def _simulate_interest_rate_shock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate interest rate increase impact.
        
        Higher rates -> Higher debt service -> Lower DSCR -> Higher risk
        
        Args:
            params: {"rate_increase_bps": 200}  # 2% increase
        
        Returns:
            Impact analysis
        """
        rate_increase_bps = params.get("rate_increase_bps", 200)
        rate_increase_pct = rate_increase_bps / 100  # Convert to percentage
        
        # Impact calculations
        impacted_smes = []
        new_critical_smes = []
        risk_score_increases = []
        
        for _, sme in self.smes_df.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            debt = float(sme['debt'])
            ebitda = float(sme['ebitda'])
            
            # Calculate new interest expense (simplified)
            current_interest = debt * 0.05  # Assume 5% base rate
            new_interest = debt * (0.05 + rate_increase_pct / 100)
            interest_increase = new_interest - current_interest
            
            # Impact on DSCR
            new_ebitda_after_interest = ebitda - interest_increase
            
            # Estimate risk score increase
            # High debt companies are more impacted
            debt_ratio = debt / max(float(sme['revenue']), 1)
            impact_multiplier = min(debt_ratio * 10, 25)  # Cap at 25 points
            
            risk_increase = impact_multiplier
            new_risk_score = min(current_risk + risk_increase, 100)
            
            if risk_increase >= 5:  # Materially impacted
                impacted_smes.append({
                    "id": sme_id,
                    "name": sme['name'],
                    "current_risk": current_risk,
                    "new_risk": int(new_risk_score),
                    "risk_increase": int(risk_increase),
                    "exposure": float(sme['exposure']),
                    "debt": debt
                })
                
                risk_score_increases.append(risk_increase)
                
                # Check if moved to critical
                if current_risk < 60 and new_risk_score >= 60:
                    new_critical_smes.append({
                        "id": sme_id,
                        "name": sme['name'],
                        "new_risk": int(new_risk_score),
                        "exposure": float(sme['exposure'])
                    })
        
        # Calculate aggregate impact
        total_impacted_exposure = sum(s['exposure'] for s in impacted_smes)
        total_new_critical_exposure = sum(s['exposure'] for s in new_critical_smes)
        avg_risk_increase = sum(risk_score_increases) / len(risk_score_increases) if risk_score_increases else 0
        
        return {
            "scenario": "Interest Rate Shock",
            "parameters": {
                "rate_increase_bps": rate_increase_bps,
                "rate_increase_pct": round(rate_increase_pct, 2)
            },
            "impact": {
                "smes_materially_affected": len(impacted_smes),
                "total_impacted_exposure": total_impacted_exposure,
                "avg_risk_score_increase": round(avg_risk_increase, 1),
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": total_new_critical_exposure,
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.35, 1),  # 35% of new critical
                "estimated_loss": round(total_new_critical_exposure * 0.35 * 0.45, 2)  # 35% PD * 45% LGD
            },
            "top_impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:10],
            "new_critical_smes": new_critical_smes
        }
    
    async def _simulate_sector_shock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate sector-specific shock (e.g., retail downturn, construction crisis).
        
        Args:
            params: {"sector": "Retail/Fashion", "revenue_impact_pct": -20}
        
        Returns:
            Sector impact analysis
        """
        sector = params.get("sector", "Retail/Fashion")
        revenue_impact_pct = params.get("revenue_impact_pct", -20)
        
        # Get sector SMEs
        sector_smes = self.smes_df[self.smes_df['sector'] == sector]
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in sector_smes.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            revenue = float(sme['revenue'])
            
            # Revenue shock impacts operational score significantly
            # Negative revenue growth adds 20-30 points typically
            risk_increase = abs(revenue_impact_pct) * 1.5  # 20% decline = 30 points
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": int(risk_increase),
                "exposure": float(sme['exposure']),
                "revenue": revenue
            })
            
            # Check if moved to critical
            if current_risk < 60 and new_risk_score >= 60:
                new_critical_smes.append({
                    "id": sme_id,
                    "name": sme['name'],
                    "new_risk": int(new_risk_score),
                    "exposure": float(sme['exposure'])
                })
        
        total_sector_exposure = sum(s['exposure'] for s in impacted_smes)
        total_new_critical_exposure = sum(s['exposure'] for s in new_critical_smes)
        
        return {
            "scenario": "Sector Shock",
            "parameters": {
                "sector": sector,
                "revenue_impact_pct": revenue_impact_pct
            },
            "impact": {
                "total_smes_in_sector": len(sector_smes),
                "total_sector_exposure": total_sector_exposure,
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": total_new_critical_exposure,
                "pct_of_sector_critical": round(len(new_critical_smes) / len(sector_smes) * 100, 1),
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.4, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.4 * 0.45, 2)
            },
            "impacted_smes": sorted(impacted_smes, key=lambda x: x['new_risk'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes
        }
    
    async def _simulate_recession(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate economic recession (affects all SMEs).
        
        Args:
            params: {"severity": "moderate", "duration_months": 12}
                    severity: mild, moderate, severe
        
        Returns:
            Portfolio-wide impact
        """
        severity = params.get("severity", "moderate")
        duration_months = params.get("duration_months", 12)
        
        # Map severity to impact factors
        severity_factors = {
            "mild": {"revenue_impact": -5, "base_risk_increase": 5},
            "moderate": {"revenue_impact": -15, "base_risk_increase": 15},
            "severe": {"revenue_impact": -30, "base_risk_increase": 30}
        }
        
        factor = severity_factors.get(severity, severity_factors["moderate"])
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in self.smes_df.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            sector = sme['sector']
            
            # Different sectors react differently to recession
            sector_multipliers = {
                "Software/Technology": 0.7,  # More resilient
                "Healthcare": 0.6,
                "Energy/Utilities": 0.8,
                "Manufacturing": 1.2,
                "Retail/Fashion": 1.5,  # More vulnerable
                "Food/Hospitality": 1.4,
                "Construction": 1.8,
                "Marketing Services": 1.3
            }
            
            multiplier = sector_multipliers.get(sector, 1.0)
            risk_increase = factor["base_risk_increase"] * multiplier
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "sector": sector,
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": int(risk_increase),
                "exposure": float(sme['exposure'])
            })
            
            # Check if moved to critical
            if current_risk < 60 and new_risk_score >= 60:
                new_critical_smes.append({
                    "id": sme_id,
                    "name": sme['name'],
                    "sector": sector,
                    "new_risk": int(new_risk_score),
                    "exposure": float(sme['exposure'])
                })
        
        total_exposure = sum(s['exposure'] for s in impacted_smes)
        total_new_critical_exposure = sum(s['exposure'] for s in new_critical_smes)
        
        return {
            "scenario": "Economic Recession",
            "parameters": {
                "severity": severity,
                "duration_months": duration_months,
                "expected_revenue_impact": f"{factor['revenue_impact']}%"
            },
            "impact": {
                "total_portfolio_exposure": total_exposure,
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": total_new_critical_exposure,
                "pct_of_portfolio_critical": round(len(new_critical_smes) / len(self.smes_df) * 100, 1),
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.45, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.45 * 0.45, 2)
            },
            "most_vulnerable_sectors": self._get_vulnerable_sectors(new_critical_smes),
            "top_impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes[:20]
        }
    
    async def _simulate_regulation_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate regulatory change impact (e.g., new legislation affecting specific sector).
        
        Args:
            params: {
                "regulation": "Hemp Products Ban",
                "affected_sectors": ["Food/Hospitality", "Retail/Fashion"],
                "revenue_at_risk_pct": 40
            }
        
        Returns:
            Regulation impact analysis
        """
        regulation = params.get("regulation", "New Regulation")
        affected_sectors = params.get("affected_sectors", [])
        revenue_at_risk_pct = params.get("revenue_at_risk_pct", 30)
        
        # Find affected SMEs
        affected_smes = self.smes_df[self.smes_df['sector'].isin(affected_sectors)]
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in affected_smes.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            
            # Regulation risk adds 10-40 points depending on revenue exposure
            risk_increase = revenue_at_risk_pct * 1.2  # 40% revenue at risk = 48 points
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "sector": sme['sector'],
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": int(risk_increase),
                "exposure": float(sme['exposure']),
                "revenue_at_risk": float(sme['revenue']) * revenue_at_risk_pct / 100
            })
            
            if current_risk < 60 and new_risk_score >= 60:
                new_critical_smes.append({
                    "id": sme_id,
                    "name": sme['name'],
                    "sector": sme['sector'],
                    "new_risk": int(new_risk_score),
                    "exposure": float(sme['exposure'])
                })
        
        total_impacted_exposure = sum(s['exposure'] for s in impacted_smes)
        total_new_critical_exposure = sum(s['exposure'] for s in new_critical_smes)
        
        return {
            "scenario": "Regulatory Change",
            "parameters": {
                "regulation": regulation,
                "affected_sectors": affected_sectors,
                "revenue_at_risk_pct": revenue_at_risk_pct
            },
            "impact": {
                "smes_affected": len(impacted_smes),
                "total_impacted_exposure": total_impacted_exposure,
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": total_new_critical_exposure,
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.5, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.5 * 0.45, 2)
            },
            "impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes
        }
    
    def _get_vulnerable_sectors(self, critical_smes: List[Dict]) -> List[Dict]:
        """Get sectors most vulnerable in scenario."""
        sector_counts = {}
        sector_exposures = {}
        
        for sme in critical_smes:
            sector = sme['sector']
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
            sector_exposures[sector] = sector_exposures.get(sector, 0) + sme['exposure']
        
        vulnerable = []
        for sector in sector_counts:
            vulnerable.append({
                "sector": sector,
                "new_critical_count": sector_counts[sector],
                "new_critical_exposure": sector_exposures[sector]
            })
        
        return sorted(vulnerable, key=lambda x: x['new_critical_count'], reverse=True)


# Singleton instance
_scenario_service = None

def get_scenario_service() -> ScenarioService:
    """Get singleton scenario service instance."""
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service