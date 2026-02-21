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
            parameters: Scenario parameters e.g. {"rate_change": 1.0, "sector": "retail"}
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
                # POC fallback — representative sample by scenario type
                fallback = {
                    "interest_rate": ["0142", "0234", "0456", "0531", "0789"],
                    "regulation":    ["0445", "0672", "0823"],
                    "sector_shock":  ["0142", "0287", "0531", "0672"],
                    "economic":      ["0142", "0234", "0287", "0531", "0789"],
                    "geographic":    ["0142", "0456", "0823"],
                }
                sme_ids = fallback.get(scenario_type, ["0142", "0287", "0531"])
                return {"sme_ids": sme_ids, "source": "fallback", "total": len(sme_ids)}

    async def calculate_portfolio_impact(
        scenario_type: str,
        parameters: Dict[str, Any],
        sme_ids: List[str],
    ) -> Dict[str, Any]:
        """Calculate portfolio-level impact of a scenario across affected SMEs.

        The backend risk engine applies scenario parameters to each SME's
        current risk profile and returns before/after comparisons.

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
                # POC inline fallback — simple additive model
                impact_delta = _estimate_impact_delta(scenario_type, parameters)
                impacts = []
                for sme_id in sme_ids:
                    clean = sme_id.replace("#", "")
                    # Base score placeholder — real values come from backend
                    base_score = 55
                    new_score  = min(100, max(0, base_score + impact_delta))
                    impacts.append({
                        "sme_id": f"#{clean}",
                        "score_before": base_score,
                        "score_after":  new_score,
                        "change":       new_score - base_score,
                        "category_before": _score_category(base_score),
                        "category_after":  _score_category(new_score),
                    })

                critical_delta = sum(
                    1 for i in impacts
                    if i["category_after"] == "critical" and i["category_before"] != "critical"
                )
                return {
                    "portfolio_summary": {
                        "total_affected":   len(impacts),
                        "critical_increase": critical_delta,
                        "avg_score_change":  round(impact_delta, 1),
                        "source":            "fallback",
                    },
                    "sme_impacts": sorted(impacts, key=lambda x: x["change"], reverse=True),
                }

    return [identify_affected_smes, calculate_portfolio_impact]


def _estimate_impact_delta(scenario_type: str, parameters: Dict[str, Any]) -> float:
    """Simple heuristic for POC fallback when backend is unavailable."""
    if scenario_type == "interest_rate":
        return parameters.get("rate_change", 1.0) * 8
    elif scenario_type == "sector_shock":
        return parameters.get("severity", 0.5) * 20
    elif scenario_type == "economic":
        return parameters.get("gdp_change", -1.0) * -5
    return 10.0


def _score_category(score: int) -> str:
    if score >= 80:  return "critical"
    elif score >= 50:return "medium"
    return "stable"


class ScenarioAgent:
    """Scenario Simulation Agent — runs what-if analysis across the SME portfolio"""

    def __init__(self):
        self.config = get_config()

        # MCPToolset gives the agent access to per-SME data signals
        # (financials, compliance, employees, news) for contextualising
        # scenario impacts when narrating results.
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

    async def simulate(self, scenario_description: str, session_id: str = None) -> Dict[str, Any]:
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

            prompt = f"""Analyse this scenario and run a complete portfolio simulation:

Scenario: {scenario_description}

Steps:
1. Parse the scenario — identify type (interest_rate / regulation / sector_shock / economic / geographic) and extract numeric parameters
2. Call identify_affected_smes with the type and parameters
3. Call calculate_portfolio_impact with the type, parameters, and the sme_ids returned in step 2
4. For the top 3 most impacted SMEs, call assess_financial_health and assess_news_risk to add narrative colour
5. Summarise with clear before/after portfolio numbers and the top 5 most impacted SMEs
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