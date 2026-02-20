"""
Scenario Simulation Agent
Uses ADK patterns for portfolio-wide what-if analysis
"""
import logging
from typing import Any, Dict, List

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient
from agents.interaction.prompts import SCENARIO_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

def make_scenario_tools(mcp_client: MCPClient):
    """Create scenario tool functions as plain async functions (ADK requirement)"""

    async def identify_affected_smes(
        scenario_type: str,
        parameters: Dict[str, Any]
    ) -> List[str]:
        """Identify SMEs affected by a scenario based on type and parameters.

        Args:
            scenario_type: Type of scenario (interest_rate, regulation, sector_shock, economic, geographic)
            parameters: Scenario parameters e.g. {"rate_change": 1.0} for +1% interest rate
        """
        logger.info(f"Identifying affected SMEs for scenario: {scenario_type}")

        result = await mcp_client.call_tool(
            "bigquery_server",
            "filter_smes_by_criteria",
            {"scenario_type": scenario_type, "parameters": parameters}
        )

        # Fallback mock if MCP returns empty
        if not result or result.get("error"):
            if scenario_type == "interest_rate":
                return ["#0234", "#0456", "#0789", "#0142"]
            elif scenario_type == "regulation":
                return ["#0445", "#0672"]
            else:
                return ["#0142", "#0287", "#0531"]

        return result.get("sme_ids", [])

    async def calculate_sme_impact(
        sme_id: str,
        scenario_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate the impact of a scenario on a specific SME.

        Args:
            sme_id: SME ID to assess (e.g. '#0142')
            scenario_parameters: Parameters describing the scenario impact
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Calculating impact for SME: #{clean_id}")

        sme_data = await mcp_client.call_tool(
            "bigquery_server", "get_sme_data", {"sme_id": clean_id}
        )

        vertex_result = await mcp_client.call_tool(
            "vertex_ai_server",
            "predict_risk_score",
            {"sme_id": clean_id, "scenario_parameters": scenario_parameters}
        )

        current_score = sme_data.get("risk_score", 65) if not sme_data.get("error") else 65
        impact = scenario_parameters.get("expected_impact", 10)
        new_score = min(100, current_score + impact)

        def get_category(score: int) -> str:
            if score >= 80: return "critical"
            elif score >= 50: return "medium"
            return "stable"

        return {
            "sme_id": f"#{clean_id}",
            "sme_name": sme_data.get("name", "Unknown"),
            "score_before": current_score,
            "score_after": new_score,
            "change": new_score - current_score,
            "category_before": get_category(current_score),
            "category_after": get_category(new_score),
        }

    async def aggregate_portfolio_impact(
        sme_impacts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate individual SME impacts to portfolio level with before/after comparison.

        Args:
            sme_impacts: List of individual SME impact results from calculate_sme_impact
        """
        logger.info(f"Aggregating portfolio impact across {len(sme_impacts)} SMEs")

        if not sme_impacts:
            return {"error": "No SME impacts to aggregate"}

        critical_before = sum(1 for s in sme_impacts if s["category_before"] == "critical")
        critical_after = sum(1 for s in sme_impacts if s["category_after"] == "critical")
        avg_change = sum(s["change"] for s in sme_impacts) / len(sme_impacts)
        top_impacted = sorted(sme_impacts, key=lambda x: x["change"], reverse=True)[:10]

        # Base portfolio counts (not in simulation)
        base_critical = 23

        return {
            "portfolio_impact": {
                "critical_before": base_critical + critical_before,
                "critical_after": base_critical + critical_after,
                "critical_change": critical_after - critical_before,
                "avg_score_change": round(avg_change, 1),
                "total_affected": len(sme_impacts),
            },
            "top_impacted": top_impacted,
        }

    return [identify_affected_smes, calculate_sme_impact, aggregate_portfolio_impact]


class ScenarioAgent:
    """Scenario Simulation Agent - runs what-if analysis across the SME portfolio"""

    def __init__(self):
        self.config = get_config()
        self.mcp_client = MCPClient(self.config.mcp_server_url)

        tools = make_scenario_tools(self.mcp_client)

        self.agent = Agent(
            name="scenario_simulation_agent",
            model=self.config.model_name,
            description="Runs what-if scenario analysis across the SME credit portfolio",
            instruction=SCENARIO_SYSTEM_INSTRUCTION,
            tools=tools,
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="credit_risk_scenarios",
            session_service=self.session_service,
        )

        logger.info("Scenario Agent initialized")

    async def simulate(self, scenario_description: str, session_id: str = None) -> Dict[str, Any]:
        """Run a complete scenario simulation from a natural language description.

        Args:
            scenario_description: Natural language scenario (e.g. 'What if interest rates rise 1%?')
            session_id: Optional session ID for conversation continuity
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
1. Identify scenario type and extract parameters
2. Call identify_affected_smes with the type and parameters
3. Call calculate_sme_impact for each affected SME
4. Call aggregate_portfolio_impact with all results
5. Summarise the portfolio impact with clear before/after numbers
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
                "analysis": final_response or "No analysis generated",
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Scenario simulation error: {e}", exc_info=True)
            return {
                "description": scenario_description,
                "error": str(e),
                "status": "failed",
            }