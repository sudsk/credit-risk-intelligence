"""
Scenario Service
Runs stress test scenarios using bank's pre-calculated vectors.

Methodology (aligned to ESRB/EBA adverse scenario framework):
- Applies known macro→PD vectors per sector, not flat portfolio averages
- All results labelled as ESTIMATED — not a re-run of the bank's full stress model
- Loss projections use LGD assumption of 45% (standard SME unsecured)
- Reserve recommendations use 1.5x additional expected loss as provision buffer
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "mcp-servers" / "data"
SMES_CSV = DATA_DIR / "smes.csv"

# Loss Given Default assumption for SME unsecured lending
LGD = 0.45

# ── Stress test vectors ────────────────────────────────────────────────────
# Source: EBA/ESRB adverse scenario framework + standard CCAR vectors
# Each vector defines: base portfolio PD increase (%) + per-sector multipliers
# Multiplier > 1 = sector more sensitive than average
# Multiplier < 1 = sector less sensitive (defensive)

STRESS_TEST_VECTORS = {
    "interest_rate": {
        "100_bps": {"portfolio_pd_increase": 2.5},
        "200_bps": {"portfolio_pd_increase": 5.0},
        "300_bps": {"portfolio_pd_increase": 8.0},
    },
    "recession": {
        "mild":     {"portfolio_pd_increase": 3.0},
        "moderate": {"portfolio_pd_increase": 7.0},
        "severe":   {"portfolio_pd_increase": 12.0},
    },
}

# Sector sensitivity multipliers — applied on top of base PD increase
# Derived from historical EBA stress test disclosures
SECTOR_MULTIPLIERS: Dict[str, float] = {
    "Construction":         1.5,
    "Retail/Fashion":       1.3,
    "Food/Hospitality":     1.25,
    "Manufacturing":        1.1,
    "Marketing Services":   1.0,
    "Transportation":       1.0,
    "Logistics":            1.0,
    "Software/Technology":  0.8,
    "Professional Services":0.7,
    "Energy/Utilities":     0.85,
    "Healthcare":           0.6,
}

# GDP → PD mapping: each 1% GDP contraction → ~2% PD increase (EBA baseline)
GDP_PD_FACTOR = 2.0

# Unemployment → PD mapping: each 1pp unemployment rise → ~1.5% PD increase
UNEMPLOYMENT_PD_FACTOR = 1.5

# Real estate shock → Construction/Food/Hospitality exposure factor
REAL_ESTATE_SECTORS = {"Construction", "Food/Hospitality"}
REAL_ESTATE_PD_FACTOR = 0.15   # 15% real estate price drop → 1pp PD for exposed sectors

# ── Recommendation tier thresholds ────────────────────────────────────────
# Per Jeremy/Sandro 2 Feb: Ultra / Conservative / Moderate tiers

TIER_THRESHOLDS = {
    "ultra_conservative": {"min_new_critical": 20, "min_loss_gbp": 10_000_000},
    "conservative":       {"min_new_critical": 10, "min_loss_gbp":  5_000_000},
    # below conservative thresholds = moderate
}

TIER_TIMELINES = {
    "ultra_conservative": "30 days",
    "conservative":       "60 days",
    "moderate":           "90 days / ongoing monitoring",
}

# Reserve multiplier: 1.5x additional expected loss
RESERVE_MULTIPLIER = 1.5


class ScenarioService:
    """
    Service for scenario analysis using bank's stress test vectors.

    All outputs are ESTIMATED using pre-calibrated macro→PD vectors.
    This does NOT re-run the bank's full CCAR/ICAAP model.
    """

    def __init__(self):
        self.smes_df = pd.read_csv(SMES_CSV)
        logger.info(f"ScenarioService initialised — {len(self.smes_df)} SMEs loaded")

    async def run_scenario(
        self, scenario_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply stress test vectors to portfolio and return enriched results
        including 3-year loss projections, sector breakdown, and
        3-tier recommendations.
        """
        if scenario_type == "interest_rate":
            return await self._simulate_interest_rate_shock(parameters)
        elif scenario_type == "sector_shock":
            return await self._simulate_sector_shock(parameters)
        elif scenario_type in ("recession", "economic"):
            return await self._simulate_recession(parameters)
        elif scenario_type in ("eba_2025_adverse", "eba_adverse"):
            return await self._simulate_eba_2025_adverse(parameters)
        elif scenario_type in ("geopolitical", "climate_transition", "regulation"):
            return await self._simulate_macro_shock(parameters)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    # ── Scenario implementations ───────────────────────────────────────────

    async def _simulate_interest_rate_shock(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        rate_bps = int(params.get("rate_change", params.get("rate_increase_bps", 200)))

        # Interpolate base PD increase from vectors
        if rate_bps <= 100:
            base_pd_increase = 2.5 * (rate_bps / 100)
        elif rate_bps <= 200:
            base_pd_increase = 2.5 + 2.5 * ((rate_bps - 100) / 100)
        else:
            base_pd_increase = 5.0 + 3.0 * ((rate_bps - 200) / 100)

        impacted, new_critical, sector_map = self._apply_vectors(
            base_pd_increase, SECTOR_MULTIPLIERS
        )

        return self._build_result(
            scenario_name=f"Interest Rate Shock +{rate_bps}bps",
            parameters={"rate_change_bps": rate_bps},
            methodology=(
                f"EBA vector: +{rate_bps}bps sustained → estimated portfolio PD "
                f"+{base_pd_increase:.1f}% average. Sector multipliers applied."
            ),
            impacted=impacted,
            new_critical=new_critical,
            sector_map=sector_map,
            params=params,
        )

    async def _simulate_eba_2025_adverse(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        EBA 2025 EU-wide adverse scenario (ESRB baseline):
        - Rates +200bps
        - GDP -6% cumulative over 3 years
        - Unemployment +5pp
        - Real estate -35%
        All applied simultaneously with combined PD impact.
        """
        rate_bps   = int(params.get("rate_change", 200))
        gdp_change = float(params.get("gdp_change", -6.0))
        unemp      = float(params.get("unemployment_change", 5.0))
        re_shock   = float(params.get("real_estate_shock", -35))

        # Combine macro vectors
        pd_from_rates   = 5.0 * (rate_bps / 200)
        pd_from_gdp     = abs(gdp_change) * GDP_PD_FACTOR
        pd_from_unemp   = unemp * UNEMPLOYMENT_PD_FACTOR
        base_pd_increase = pd_from_rates + pd_from_gdp + pd_from_unemp

        # Real estate shock adds extra PD for exposed sectors
        re_multipliers = dict(SECTOR_MULTIPLIERS)
        re_extra = abs(re_shock) / 100 / REAL_ESTATE_PD_FACTOR
        for sector in REAL_ESTATE_SECTORS:
            re_multipliers[sector] = re_multipliers.get(sector, 1.0) + re_extra * 0.1

        impacted, new_critical, sector_map = self._apply_vectors(
            base_pd_increase, re_multipliers
        )

        return self._build_result(
            scenario_name="EBA 2025 Adverse — Higher for Longer",
            parameters={
                "rate_change_bps": rate_bps,
                "gdp_change_pct": gdp_change,
                "unemployment_change_pp": unemp,
                "real_estate_shock_pct": re_shock,
            },
            methodology=(
                f"EBA 2025 adverse scenario. Combined PD impact: "
                f"+{pd_from_rates:.1f}% (rates) + {pd_from_gdp:.1f}% (GDP) "
                f"+ {pd_from_unemp:.1f}% (unemployment) = {base_pd_increase:.1f}% base. "
                f"Real estate shock adds additional stress to Construction and Food/Hospitality."
            ),
            impacted=impacted,
            new_critical=new_critical,
            sector_map=sector_map,
            params=params,
        )

    async def _simulate_recession(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        gdp_change  = float(params.get("gdp_change", -3.5))
        unemp       = float(params.get("unemployment_change", 3.0))
        severity    = params.get("severity", "moderate")

        # Use explicit GDP/unemployment params if provided, else fall back to severity vector
        if gdp_change != 0 or unemp != 0:
            base_pd_increase = (
                abs(gdp_change) * GDP_PD_FACTOR +
                unemp * UNEMPLOYMENT_PD_FACTOR
            )
        else:
            vector_map = {"mild": 3.0, "moderate": 7.0, "severe": 12.0}
            base_pd_increase = vector_map.get(severity, 7.0)

        impacted, new_critical, sector_map = self._apply_vectors(
            base_pd_increase, SECTOR_MULTIPLIERS
        )

        return self._build_result(
            scenario_name=f"Recession / GDP Contraction ({severity})",
            parameters={
                "gdp_change_pct": gdp_change,
                "unemployment_change_pp": unemp,
                "severity": severity,
            },
            methodology=(
                f"GDP contraction {gdp_change}% → PD +{abs(gdp_change)*GDP_PD_FACTOR:.1f}%; "
                f"unemployment +{unemp}pp → PD +{unemp*UNEMPLOYMENT_PD_FACTOR:.1f}%. "
                f"Combined base PD increase: +{base_pd_increase:.1f}%."
            ),
            impacted=impacted,
            new_critical=new_critical,
            sector_map=sector_map,
            params=params,
        )

    async def _simulate_sector_shock(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        sector   = params.get("sector", "Retail/Fashion")
        severity = float(params.get("severity", 0.7))
        gdp_drag = float(params.get("gdp_change", -2.0))

        # Sector shock: targeted high impact on affected sector, mild on rest
        targeted_multipliers = {s: 0.3 for s in SECTOR_MULTIPLIERS}
        targeted_multipliers[sector] = 3.0 * severity

        base_pd_increase = abs(gdp_drag) * GDP_PD_FACTOR + (severity * 5)

        impacted, new_critical, sector_map = self._apply_vectors(
            base_pd_increase, targeted_multipliers
        )

        return self._build_result(
            scenario_name=f"Sector Shock — {sector}",
            parameters={"sector": sector, "severity": severity, "gdp_drag_pct": gdp_drag},
            methodology=(
                f"Sector-specific shock on {sector} (severity {severity:.1f}). "
                f"Direct sector multiplier {3.0*severity:.1f}x. "
                f"Broader GDP drag of {gdp_drag}% applied at reduced weight to rest of portfolio."
            ),
            impacted=impacted,
            new_critical=new_critical,
            sector_map=sector_map,
            params=params,
        )

    async def _simulate_macro_shock(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic handler for geopolitical, climate, regulation scenarios."""
        gdp_change  = float(params.get("gdp_change", -2.0))
        unemp       = float(params.get("unemployment_change", 1.0))
        severity    = float(params.get("severity", 0.5))
        scenario_name = params.get("scenario_name", "Macro Shock")

        base_pd_increase = (
            abs(gdp_change) * GDP_PD_FACTOR +
            unemp * UNEMPLOYMENT_PD_FACTOR +
            severity * 3
        )

        impacted, new_critical, sector_map = self._apply_vectors(
            base_pd_increase, SECTOR_MULTIPLIERS
        )

        return self._build_result(
            scenario_name=scenario_name,
            parameters=params,
            methodology=(
                f"Macro shock scenario. Estimated combined PD increase: "
                f"+{base_pd_increase:.1f}% using EBA-aligned sector vectors."
            ),
            impacted=impacted,
            new_critical=new_critical,
            sector_map=sector_map,
            params=params,
        )

    # ── Core vector application ────────────────────────────────────────────

    def _apply_vectors(
        self,
        base_pd_increase: float,
        sector_multipliers: Dict[str, float],
    ) -> Tuple[List[Dict], List[Dict], Dict[str, Dict]]:
        """
        Apply macro→PD vectors to every SME in portfolio.

        Returns:
            impacted     — all SMEs with material risk increase
            new_critical — SMEs that cross the critical threshold
            sector_map   — per-sector aggregated impact
        """
        impacted: List[Dict] = []
        new_critical: List[Dict] = []
        sector_map: Dict[str, Dict] = {}

        for _, sme in self.smes_df.iterrows():
            sector       = str(sme['sector'])
            current_risk = int(sme['risk_score'])
            exposure     = float(sme['exposure'])

            multiplier   = sector_multipliers.get(sector, 1.0)
            risk_increase = base_pd_increase * multiplier
            new_risk      = min(current_risk + risk_increase, 100)

            sme_record = {
                "smeId":       str(sme['id']),
                "smeName":     str(sme['name']),
                "sector":      sector,
                "geography":   str(sme.get('geography', 'UK')),
                "scoreBefore": current_risk,
                "scoreAfter":  round(new_risk, 1),
                "change":      round(risk_increase, 1),
                "exposure":    exposure,
                "reason":      self._reason_text(sector, base_pd_increase, multiplier),
            }

            if risk_increase >= 2.0:
                impacted.append(sme_record)

            went_critical = current_risk < 60 and new_risk >= 60
            if went_critical:
                new_critical.append(sme_record)

            # Aggregate per sector
            if sector not in sector_map:
                sector_map[sector] = {
                    "sector": sector,
                    "smes": 0,
                    "avgChange": 0.0,
                    "totalExposure": 0.0,
                    "newCritical": 0,
                    "_total_change": 0.0,
                }
            sm = sector_map[sector]
            sm["smes"]          += 1
            sm["totalExposure"] += exposure
            sm["_total_change"] += risk_increase
            if went_critical:
                sm["newCritical"] += 1

        # Finalise sector averages
        for sm in sector_map.values():
            sm["avgChange"] = round(sm["_total_change"] / sm["smes"], 1) if sm["smes"] else 0
            del sm["_total_change"]

        return impacted, new_critical, sector_map

    # ── Result builder ─────────────────────────────────────────────────────

    def _build_result(
        self,
        scenario_name: str,
        parameters: Dict[str, Any],
        methodology: str,
        impacted: List[Dict],
        new_critical: List[Dict],
        sector_map: Dict[str, Dict],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assemble the full scenario result payload including:
        - Portfolio impact summary (before/after)
        - Sector breakdown with loss per sector
        - 3-year loss projections
        - 3-tier recommendations
        """
        all_smes         = self.smes_df
        total_smes       = len(all_smes)
        critical_before  = int((all_smes['risk_category'] == 'critical').sum())
        critical_after   = critical_before + len(new_critical)

        avg_score_before = round(float(all_smes['risk_score'].mean()), 1)
        avg_score_after  = round(
            avg_score_before + (
                sum(s['change'] for s in impacted) / total_smes
                if impacted else 0
            ), 1
        )

        # PD before/after (portfolio average)
        pd_before = round(float(all_smes['pd_original'].mean()), 2) if 'pd_original' in all_smes.columns else 2.1
        pd_after  = round(pd_before * (1 + len(new_critical) / max(total_smes, 1)), 2)

        # ── Loss projections ───────────────────────────────────────────────
        # Additional expected loss = new critical exposure × PD uplift × LGD
        new_critical_exposure = sum(s['exposure'] for s in new_critical)
        pd_uplift             = len(new_critical) / max(total_smes, 1)

        # EAD = Exposure at Default; EL = PD × LGD × EAD
        additional_el_year0 = new_critical_exposure * pd_uplift * LGD
        # Years 1-3: compounding deterioration at 15% / 10% / 5% increment
        additional_el_year1 = additional_el_year0 * 1.15
        additional_el_year2 = additional_el_year0 * 1.25
        additional_el_year3 = additional_el_year0 * 1.30

        estimated_loss = {
            "current":   round(additional_el_year0),
            "year1":     round(additional_el_year1),
            "year2":     round(additional_el_year2),
            "year3":     round(additional_el_year3),
            "lgd_assumption": LGD,
            "note": "Estimated — based on EAD × PD uplift × LGD. Not a full Basel stress model.",
        }

        # ── Sector breakdown ───────────────────────────────────────────────
        sector_impact = []
        for sm in sorted(sector_map.values(), key=lambda x: x['avgChange'], reverse=True):
            sector_el = sm['totalExposure'] * (sm['newCritical'] / max(sm['smes'], 1)) * pd_uplift * LGD
            sector_impact.append({
                "sector":          sm['sector'],
                "smes":            sm['smes'],
                "avgChange":       sm['avgChange'],
                "newCritical":     sm['newCritical'],
                "totalExposure":   round(sm['totalExposure']),
                "estimatedLoss":   round(sector_el),
            })

        # ── Portfolio impact summary ───────────────────────────────────────
        portfolio_impact = {
            "criticalBefore":    critical_before,
            "criticalAfter":     critical_after,
            "avgScoreBefore":    avg_score_before,
            "avgScoreAfter":     avg_score_after,
            "defaultProbBefore": pd_before,
            "defaultProbAfter":  pd_after,
            "totalExposure":     round(float(all_smes['exposure'].sum())),
            "newCriticalExposure": round(new_critical_exposure),
        }

        # ── Recommendations ────────────────────────────────────────────────
        recommendations = self._build_recommendations(
            new_critical_count=len(new_critical),
            estimated_loss_current=additional_el_year0,
            new_critical_exposure=new_critical_exposure,
            sector_impact=sector_impact,
            params=params,
        )

        # ── Top impacted SMEs ──────────────────────────────────────────────
        top_impacted = sorted(impacted, key=lambda x: x['change'], reverse=True)[:10]

        return {
            "scenario":        scenario_name,
            "parameters":      parameters,
            "methodology":     methodology,
            "disclaimer":      (
                "⚠️ ESTIMATED IMPACT — uses pre-calibrated macro→PD vectors aligned to "
                "EBA/ESRB adverse scenario methodology. Does not re-run the bank's full "
                "CCAR/ICAAP stress model. Results indicative only."
            ),
            "portfolioImpact": portfolio_impact,
            "estimatedLoss":   estimated_loss,
            "sectorImpact":    sector_impact,
            "topImpacted":     top_impacted,
            "newCriticalSMEs": new_critical[:20],
            "recommendations": recommendations,
        }

    # ── Recommendation builder ─────────────────────────────────────────────

    def _build_recommendations(
        self,
        new_critical_count: int,
        estimated_loss_current: float,
        new_critical_exposure: float,
        sector_impact: List[Dict],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate 3-tier recommendations based on impact severity.

        Tier selection thresholds (agreed Jeremy/Sandro 2 Feb):
          Ultra-Conservative: >20 new critical OR loss >£10M
          Conservative:       10-20 new critical OR loss £5-10M
          Moderate:           <10 new critical AND loss <£5M

        Reserve formula: 1.5 × additional expected loss
        """
        # Determine warranted tier
        if (new_critical_count > TIER_THRESHOLDS["ultra_conservative"]["min_new_critical"]
                or estimated_loss_current > TIER_THRESHOLDS["ultra_conservative"]["min_loss_gbp"]):
            warranted_tier = "ultra_conservative"
        elif (new_critical_count > TIER_THRESHOLDS["conservative"]["min_new_critical"]
                or estimated_loss_current > TIER_THRESHOLDS["conservative"]["min_loss_gbp"]):
            warranted_tier = "conservative"
        else:
            warranted_tier = "moderate"

        # Top 2 most impacted sectors for sector-specific actions
        top_sectors = [s['sector'] for s in sector_impact if s['newCritical'] > 0][:2]
        top_sector_str = " and ".join(top_sectors) if top_sectors else "most exposed sectors"

        # Reserve calculations
        reserve_ultra  = round(estimated_loss_current * RESERVE_MULTIPLIER * 1.5)
        reserve_cons   = round(estimated_loss_current * RESERVE_MULTIPLIER)
        reserve_mod    = round(estimated_loss_current * RESERVE_MULTIPLIER * 0.5)

        def fmt_gbp(v: float) -> str:
            if v >= 1_000_000:
                return f"£{v/1_000_000:.1f}M"
            return f"£{v:,.0f}"

        ultra = {
            "reserveIncrease": fmt_gbp(reserve_ultra),
            "sectorAdjustments": [
                f"Stop new originations in {top_sector_str} immediately",
                f"Initiate full credit review across all {new_critical_count} newly critical SMEs",
                "Reduce maximum exposure per SME by 30% for critical category",
                "Notify board risk committee — portfolio stress threshold breached",
            ],
            "timeline":       TIER_TIMELINES["ultra_conservative"],
            "riskMitigation": "Maximum",
        }

        conservative = {
            "reserveIncrease": fmt_gbp(reserve_cons),
            "sectorAdjustments": [
                f"Reduce new lending in {top_sector_str} by 20%",
                f"Flag top {min(new_critical_count, 15)} newly critical SMEs for priority review",
                "Tighten covenant monitoring frequency to monthly for critical SMEs",
                "Prepare contingency plan for further deterioration",
            ],
            "timeline":       TIER_TIMELINES["conservative"],
            "riskMitigation": "High",
        }

        moderate = {
            "reserveIncrease": fmt_gbp(reserve_mod),
            "sectorAdjustments": [
                f"Monitor {top_sector_str} sector SMEs closely — quarterly review",
                "No immediate restriction on new lending",
                "Update portfolio watch list with newly impacted SMEs",
            ],
            "timeline":       TIER_TIMELINES["moderate"],
            "riskMitigation": "Standard",
        }

        return {
            "warranted_tier":    warranted_tier,
            "ultraConservative": ultra,
            "conservative":      conservative,
            "moderate":          moderate,
            "new_critical_count": new_critical_count,
            "estimated_loss_current": round(estimated_loss_current),
        }

    # ── Helpers ────────────────────────────────────────────────────────────

    def _reason_text(self, sector: str, base_pd: float, multiplier: float) -> str:
        """One-line reason string for top impacted SME table."""
        sensitivity = (
            "high sensitivity" if multiplier >= 1.3
            else "moderate sensitivity" if multiplier >= 1.0
            else "low sensitivity"
        )
        return (
            f"{sector} — {sensitivity} to macro shock "
            f"(sector multiplier {multiplier:.1f}×, base PD +{base_pd:.1f}%)"
        )

    def _get_vulnerable_sectors(self, critical_smes: List[Dict]) -> List[Dict]:
        """Get sectors most vulnerable in scenario — legacy helper kept for compatibility."""
        sector_counts: Dict[str, int]   = {}
        sector_exposures: Dict[str, float] = {}
        for sme in critical_smes:
            s = sme['sector']
            sector_counts[s]    = sector_counts.get(s, 0) + 1
            sector_exposures[s] = sector_exposures.get(s, 0.0) + sme['exposure']
        return sorted(
            [{"sector": s, "new_critical_count": c, "new_critical_exposure": round(sector_exposures[s], 2)}
             for s, c in sector_counts.items()],
            key=lambda x: x['new_critical_count'], reverse=True
        )


# ── Singleton ──────────────────────────────────────────────────────────────
_scenario_service = None

def get_scenario_service() -> ScenarioService:
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service