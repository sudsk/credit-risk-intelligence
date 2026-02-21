"""
Scenario Service
Runs stress test scenarios using bank's pre-calculated vectors.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "mcp-servers" / "data"
SMES_CSV = DATA_DIR / "smes.csv"

# Pre-calculated stress test vectors from bank's CCAR/ICAAP models
STRESS_TEST_VECTORS = {
    "interest_rate": {
        "100_bps": {
            "portfolio_pd_increase": 2.5,
            "sector_multipliers": {
                "Retail/Fashion": 1.2,
                "Construction": 1.5,
                "Software/Technology": 0.8,
                "Manufacturing": 1.1,
                "Food/Hospitality": 1.3,
                "Energy/Utilities": 0.9,
                "Marketing Services": 1.0,
                "Professional Services": 0.7,
                "Logistics": 1.2,
                "Healthcare": 0.6,
            }
        },
        "200_bps": {
            "portfolio_pd_increase": 5.0,
            "sector_multipliers": {
                "Retail/Fashion": 1.2,
                "Construction": 1.5,
                "Software/Technology": 0.8,
                "Manufacturing": 1.1,
                "Food/Hospitality": 1.3,
                "Energy/Utilities": 0.9,
                "Marketing Services": 1.0,
                "Professional Services": 0.7,
                "Logistics": 1.2,
                "Healthcare": 0.6,
            }
        },
        "300_bps": {
            "portfolio_pd_increase": 8.0,
            "sector_multipliers": {
                "Retail/Fashion": 1.2,
                "Construction": 1.5,
                "Software/Technology": 0.8,
                "Manufacturing": 1.1,
                "Food/Hospitality": 1.3,
                "Energy/Utilities": 0.9,
                "Marketing Services": 1.0,
                "Professional Services": 0.7,
                "Logistics": 1.2,
                "Healthcare": 0.6,
            }
        }
    },
    "recession": {
        "mild": {
            "portfolio_pd_increase": 3.0,
            "sector_multipliers": {
                "Retail/Fashion": 1.3,
                "Construction": 1.6,
                "Software/Technology": 0.7,
                "Manufacturing": 1.1,
                "Food/Hospitality": 1.2,
                "Energy/Utilities": 0.8,
                "Marketing Services": 1.4,
                "Professional Services": 0.9,
                "Logistics": 1.0,
                "Healthcare": 0.6,
            }
        },
        "moderate": {
            "portfolio_pd_increase": 7.0,
            "sector_multipliers": {
                "Retail/Fashion": 1.5,
                "Construction": 1.8,
                "Software/Technology": 0.7,
                "Manufacturing": 1.2,
                "Food/Hospitality": 1.4,
                "Energy/Utilities": 0.8,
                "Marketing Services": 1.3,
                "Professional Services": 0.9,
                "Logistics": 1.0,
                "Healthcare": 0.6,
            }
        },
        "severe": {
            "portfolio_pd_increase": 12.0,
            "sector_multipliers": {
                "Retail/Fashion": 1.8,
                "Construction": 2.2,
                "Software/Technology": 0.8,
                "Manufacturing": 1.5,
                "Food/Hospitality": 1.7,
                "Energy/Utilities": 0.9,
                "Marketing Services": 1.5,
                "Professional Services": 1.0,
                "Logistics": 1.2,
                "Healthcare": 0.7,
            }
        }
    }
}


class ScenarioService:
    """Service for scenario analysis using bank's stress test vectors."""
    
    def __init__(self):
        self.smes_df = pd.read_csv(SMES_CSV)
    
    async def run_scenario(self, scenario_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply stress test vectors to portfolio.
        Agents will generate recommendations from this data.
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
        """Apply bank's pre-calculated interest rate stress vectors"""
        rate_increase_bps = params.get("rate_increase_bps", 200)
        
        # Get pre-calculated vector from bank's stress test
        vector_key = f"{rate_increase_bps}_bps"
        vector = STRESS_TEST_VECTORS["interest_rate"].get(
            vector_key,
            STRESS_TEST_VECTORS["interest_rate"]["200_bps"]
        )
        
        base_pd_increase = vector["portfolio_pd_increase"]
        sector_multipliers = vector["sector_multipliers"]
        
        impacted_smes = []
        new_critical_smes = []
        risk_score_increases = []
        
        for _, sme in self.smes_df.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            sector = sme['sector']
            
            # Apply vector with sector multiplier
            multiplier = sector_multipliers.get(sector, 1.0)
            risk_increase = base_pd_increase * multiplier
            new_risk_score = min(current_risk + risk_increase, 100)
            
            if risk_increase >= 3:  # Materially impacted
                impacted_smes.append({
                    "id": sme_id,
                    "name": sme['name'],
                    "sector": sector,
                    "current_risk": current_risk,
                    "new_risk": int(new_risk_score),
                    "risk_increase": round(risk_increase, 1),
                    "exposure": float(sme['exposure'])
                })
                
                risk_score_increases.append(risk_increase)
                
                # Check if moved to critical
                if current_risk < 60 and new_risk_score >= 60:
                    new_critical_smes.append({
                        "id": sme_id,
                        "name": sme['name'],
                        "sector": sector,
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
                "rate_increase_pct": round(rate_increase_bps / 100, 2)
            },
            "methodology": f"Applied bank's stress vector: {base_pd_increase}% portfolio PD increase with sector-specific multipliers",
            "disclaimer": "⚠️ Uses pre-calculated stress vectors from your bank's most recent CCAR/ICAAP stress test. Does not re-run full stress test model.",
            "impact": {
                "smes_materially_affected": len(impacted_smes),
                "total_impacted_exposure": round(total_impacted_exposure, 2),
                "avg_risk_score_increase": round(avg_risk_increase, 1),
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": round(total_new_critical_exposure, 2),
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.35, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.35 * 0.45, 2)
            },
            "top_impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:10],
            "new_critical_smes": new_critical_smes
        }
    
    async def _simulate_sector_shock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sector-specific shock"""
        sector = params.get("sector", "Retail/Fashion")
        revenue_impact_pct = params.get("revenue_impact_pct", -20)
        
        # Get sector SMEs
        sector_smes = self.smes_df[self.smes_df['sector'] == sector]
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in sector_smes.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            
            # Revenue shock impact (simplified model)
            risk_increase = abs(revenue_impact_pct) * 1.2
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": round(risk_increase, 1),
                "exposure": float(sme['exposure'])
            })
            
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
                "total_sector_exposure": round(total_sector_exposure, 2),
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": round(total_new_critical_exposure, 2),
                "pct_of_sector_critical": round(len(new_critical_smes) / len(sector_smes) * 100, 1) if len(sector_smes) > 0 else 0,
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.4, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.4 * 0.45, 2)
            },
            "impacted_smes": sorted(impacted_smes, key=lambda x: x['new_risk'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes
        }
    
    async def _simulate_recession(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply bank's recession stress vectors"""
        severity = params.get("severity", "moderate")
        duration_months = params.get("duration_months", 12)
        
        # Get pre-calculated vector
        vector = STRESS_TEST_VECTORS["recession"].get(
            severity,
            STRESS_TEST_VECTORS["recession"]["moderate"]
        )
        
        base_pd_increase = vector["portfolio_pd_increase"]
        sector_multipliers = vector["sector_multipliers"]
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in self.smes_df.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            sector = sme['sector']
            
            # Apply vector with sector multiplier
            multiplier = sector_multipliers.get(sector, 1.0)
            risk_increase = base_pd_increase * multiplier
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "sector": sector,
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": round(risk_increase, 1),
                "exposure": float(sme['exposure'])
            })
            
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
                "duration_months": duration_months
            },
            "methodology": f"Applied bank's {severity} recession vector: {base_pd_increase}% portfolio PD increase",
            "disclaimer": "⚠️ Uses pre-calculated stress vectors from your bank's most recent stress test.",
            "impact": {
                "total_portfolio_exposure": round(total_exposure, 2),
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": round(total_new_critical_exposure, 2),
                "pct_of_portfolio_critical": round(len(new_critical_smes) / len(self.smes_df) * 100, 1),
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.45, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.45 * 0.45, 2)
            },
            "most_vulnerable_sectors": self._get_vulnerable_sectors(new_critical_smes),
            "top_impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes[:20]
        }
    
    async def _simulate_regulation_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate regulatory change impact"""
        regulation = params.get("regulation", "New Regulation")
        affected_sectors = params.get("affected_sectors", [])
        revenue_at_risk_pct = params.get("revenue_at_risk_pct", 30)
        
        affected_smes = self.smes_df[self.smes_df['sector'].isin(affected_sectors)]
        
        impacted_smes = []
        new_critical_smes = []
        
        for _, sme in affected_smes.iterrows():
            sme_id = sme['id']
            current_risk = int(sme['risk_score'])
            
            # Regulation risk impact
            risk_increase = revenue_at_risk_pct * 1.0
            new_risk_score = min(current_risk + risk_increase, 100)
            
            impacted_smes.append({
                "id": sme_id,
                "name": sme['name'],
                "sector": sme['sector'],
                "current_risk": current_risk,
                "new_risk": int(new_risk_score),
                "risk_increase": round(risk_increase, 1),
                "exposure": float(sme['exposure'])
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
                "total_impacted_exposure": round(total_impacted_exposure, 2),
                "new_critical_count": len(new_critical_smes),
                "new_critical_exposure": round(total_new_critical_exposure, 2),
                "estimated_additional_defaults": round(len(new_critical_smes) * 0.5, 1),
                "estimated_loss": round(total_new_critical_exposure * 0.5 * 0.45, 2)
            },
            "impacted_smes": sorted(impacted_smes, key=lambda x: x['risk_increase'], reverse=True)[:15],
            "new_critical_smes": new_critical_smes
        }
    
    def _get_vulnerable_sectors(self, critical_smes: List[Dict]) -> List[Dict]:
        """Get sectors most vulnerable in scenario"""
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
                "new_critical_exposure": round(sector_exposures[sector], 2)
            })
        
        return sorted(vulnerable, key=lambda x: x['new_critical_count'], reverse=True)


# Singleton
_scenario_service = None

def get_scenario_service() -> ScenarioService:
    """Get singleton scenario service instance"""
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service