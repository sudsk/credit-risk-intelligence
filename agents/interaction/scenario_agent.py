"""
Scenario Simulation Agent
Portfolio-wide what-if analysis.
ADK 1.25.0 with MCPToolset for direct MCP server access.
"""
import logging
from typing import Any, Dict, List

import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.interaction.prompts import SCENARIO_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


def make_scenario_tools(config):
    """
    Scenario tools. The agent uses MCPToolset to fetch per-SME signals
    (financials, employees, compliance) then these tools handle the
    portfolio-level scenario maths that the backend risk engine computes.
    """

    async def identify_affected_smes(
        scenario_type: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Identify SMEs affected by a scenario based on type and parameters.

        Args:
            scenario_type: interest_rate | regulation | sector_shock | economic | geographic
            parameters: Scenario parameters e.g. {"rate_change": 200, "sector": "Retail/Fashion"}
        """
        logger.info(f"Identifying affected SMEs: {scenario_type} {parameters}")
        async with httpx.AsyncClient(timeout=30.0) as http:
            try:
                response = await http.post(
                    f"{config.backend_api_url}/api/v1/scenarios/affected-smes",
                    json={"scenario_type": scenario_type, "parameters": parameters},
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Backend filter failed, using fallback: {e}")
                fallback = {
                    "interest_rate":   ["0142", "0234", "0456", "0531", "0789"],
                    "regulation":      ["0445", "0672", "0823"],
                    "sector_shock":    ["0142", "0287", "0531", "0672"],
                    "economic":        ["0142", "0234", "0287", "0531", "0789"],
                    "eba_2025_adverse":["0142", "0234", "0445", "0531", "0672", "0789"],
                    "geographic":      ["0142", "0456", "0823"],
                }
                sme_ids = fallback.get(scenario_type, ["0142", "0287", "0531"])
                return {"sme_ids": sme_ids, "source": "fallback", "total": len(sme_ids)}

    async def calculate_portfolio_impact(
        scenario_type: str,
        parameters: Dict[str, Any],
        sme_ids: List[str],
    ) -> Dict[str, Any]:
        """Calculate portfolio-level impact of a scenario across affected SMEs.

        Returns structured result including portfolioImpact, estimatedLoss,
        sectorImpact, topImpacted, and 3-tier recommendations.

        Args:
            scenario_type: Type of scenario
            parameters: Scenario parameters
            sme_ids: List of affected SME IDs (from identify_affected_smes)
        """
        logger.info(f"Calculating portfolio impact for {len(sme_ids)} SMEs")
        async with httpx.AsyncClient(timeout=60.0) as http:
            try:
                response = await http.post(
                    f"{config.backend_api_url}/api/v1/scenarios/calculate-impact",
                    json={
                        "scenario_type": scenario_type,
                        "parameters": parameters,
                        "sme_ids": sme_ids,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Backend impact calc failed, using inline scoring: {e}")
                impact_delta = _estimate_impact_delta(scenario_type, parameters)
                impacts = []
                for sme_id in sme_ids:
                    clean      = sme_id.replace("#", "")
                    base_score = 55
                    new_score  = min(100, max(0, base_score + impact_delta))
                    impacts.append({
                        "smeId":       f"#{clean}",
                        "smeName":     f"SME {clean}",
                        "scoreBefore": base_score,
                        "scoreAfter":  int(new_score),
                        "change":      round(new_score - base_score, 1),
                        "reason":      f"Estimated impact from {scenario_type} scenario",
                    })

                critical_delta = sum(
                    1 for i in impacts
                    if i["scoreAfter"] >= 60 and i["scoreBefore"] < 60
                )
                return {
                    "portfolioImpact": {
                        "criticalBefore":    13,
                        "criticalAfter":     13 + critical_delta,
                        "avgScoreBefore":    48,
                        "avgScoreAfter":     round(48 + impact_delta, 1),
                        "defaultProbBefore": 2.1,
                        "defaultProbAfter":  round(2.1 * 1.3, 2),
                    },
                    "estimatedLoss": {
                        "current": 0,
                        "year1":   0,
                        "year2":   0,
                        "year3":   0,
                        "note":    "Fallback — backend unavailable",
                    },
                    "sectorImpact":  [],
                    "topImpacted":   sorted(impacts, key=lambda x: x["change"], reverse=True)[:10],
                    "recommendations": {
                        "warranted_tier":    "moderate",
                        "ultraConservative": {"reserveIncrease": "N/A", "sectorAdjustments": [], "timeline": "30 days", "riskMitigation": "Maximum"},
                        "conservative":      {"reserveIncrease": "N/A", "sectorAdjustments": [], "timeline": "60 days", "riskMitigation": "High"},
                        "moderate":          {"reserveIncrease": "N/A", "sectorAdjustments": ["Monitor closely"], "timeline": "90 days", "riskMitigation": "Standard"},
                    },
                    "source": "fallback",
                }

    return [identify_affected_smes, calculate_portfolio_impact]


def _estimate_impact_delta(scenario_type: str, parameters: Dict[str, Any]) -> float:
    """Simple heuristic for POC fallback when backend is unavailable."""
    if scenario_type == "interest_rate":
        return parameters.get("rate_change", 200) / 100 * 4
    elif scenario_type == "sector_shock":
        return parameters.get("severity", 0.5) * 20
    elif scenario_type in ("recession", "economic"):
        return abs(parameters.get("gdp_change", -3.5)) * 2.5
    elif scenario_type == "eba_2025_adverse":
        return 18.0
    return 10.0


class ScenarioAgent:
    """Scenario Simulation Agent — runs what-if analysis across the SME portfolio."""

    def __init__(self):
        self.config = get_config()

        mcp_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=self.config.mcp_server_url + "/mcp",
            )
        )

        extra_tools = make_scenario_tools(self.config)

        self.agent = Agent(
            name="scenario_simulation_agent",
            model=self.config.model_name,
            description="Runs what-if scenario analysis across the SME credit portfolio",
            instruction=SCENARIO_SYSTEM_INSTRUCTION,
            tools=[mcp_toolset, *extra_tools],
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="credit_risk_scenarios",
            session_service=self.session_service,
        )

        logger.info("Scenario Agent initialised")

    async def simulate(
        self, scenario_description: str, session_id: str = None
    ) -> Dict[str, Any]:
        """Run a complete scenario simulation from a natural language description.

        Args:
            scenario_description: e.g. 'What if interest rates rise 2%?'
            session_id: Optional session ID for continuity
        """
        import uuid
        session_id = session_id or str(uuid.uuid4())
        logger.info(f"Simulating scenario [{session_id}]: {scenario_description}")

        try:
            await self.session_service.create_session(
                app_name="credit_risk_scenarios",
                user_id="system",
                session_id=session_id,
            )

            # ── Structured prompt — enforces fixed response schema ─────────
            # The schema ensures the frontend can always parse:
            #   - score before/after with delta
            #   - top 3 signals with point impact
            #   - 3-tier recommendation blocks with reserve £ and timeline
            # Any deviation from this format breaks the ScenarioResults UI.
            prompt = f"""Analyse this scenario and run a complete portfolio simulation.

Scenario: {scenario_description}

Steps:
1. Parse the scenario — identify type (interest_rate / eba_2025_adverse / sector_shock / recession / geopolitical / climate_transition) and extract numeric parameters
2. Call identify_affected_smes with the type and parameters
3. Call calculate_portfolio_impact with the type, parameters, and the sme_ids returned

Then respond using EXACTLY this structure — do not deviate from the headings or format:

---

## Scenario: [name]
**Parameters:** [key params e.g. Rate +200bps | GDP -6% | Unemployment +5pp]
**Methodology:** [one sentence from the result methodology field]

## Portfolio Impact
- Critical SMEs: [criticalBefore] → [criticalAfter] (+[delta])
- Avg Risk Score: [avgScoreBefore] → [avgScoreAfter]
- Default Probability: [defaultProbBefore]% → [defaultProbAfter]%

## Estimated Loss Projection ⚠️ Estimated
- Current year: [estimatedLoss.current formatted as £X.XM]
- Year 1: [year1 formatted as £X.XM]
- Year 2: [year2 formatted as £X.XM]
- Year 3: [year3 formatted as £X.XM]

## Top 5 Most Impacted SMEs
[rank]. [smeName] — Score [scoreBefore]→[scoreAfter] (+[change]pts) | [reason one line]

## Sector Breakdown
- [sector]: avg score +[avgChange]pts | [newCritical] newly critical | est. loss £[estimatedLoss]

## Recommended Actions
Warranted tier: **[warranted_tier]** ([new_critical_count] newly critical SMEs | est. loss [estimated_loss_current])

**Ultra-Conservative** — [reserveIncrease] reserve increase | Act within [timeline]
[sectorAdjustments as bullet list]

**Conservative** — [reserveIncrease] reserve increase | Act within [timeline]
[sectorAdjustments as bullet list]

**Moderate** — [reserveIncrease] reserve increase | [timeline]
[sectorAdjustments as bullet list]

---

⚠️ All figures are estimated using EBA/ESRB-aligned macro vectors. Not a re-run of the bank's full stress model.
"""

            content = Content(parts=[Part(text=prompt)], role="user")
            final_response = None

            async for event in self.runner.run_async(
                user_id="system",
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    break

            return {
                "description": scenario_description,
                "analysis":    final_response or "No analysis generated",
                "status":      "completed",
            }

        except Exception as e:
            logger.error(f"Scenario simulation error: {e}", exc_info=True)
            return {
                "description": scenario_description,
                "error":       str(e),
                "status":      "failed",
            }