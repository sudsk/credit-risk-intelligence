"""
SME Analysis Agent
Deep dive analysis of individual SME health.
ADK 1.25.0 with MCPToolset for direct MCP server access.
"""
import logging
from typing import Any, Dict

import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.interaction.prompts import SME_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


def make_sme_tools(config):
    """
    Non-MCP tools for the SME agent.

    Core data tools (get_financial_metrics, assess_financial_health,
    get_employee_count, get_recent_departures, get_company_info,
    assess_digital_presence, assess_news_risk, etc.) come from MCPToolset
    automatically — the agent can call them directly.

    These supplementary tools handle things the data_server doesn't provide.
    """

    async def get_peer_comparison(sme_id: str) -> Dict[str, Any]:
        """Compare an SME to sector peers in the portfolio using the backend risk engine.

        Args:
            sme_id: SME ID to compare (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching peer comparison for SME: #{clean_id}")
        async with httpx.AsyncClient(timeout=30.0) as http:
            try:
                response = await http.get(
                    f"{config.backend_api_url}/api/v1/sme/{clean_id}/peers",
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Peer comparison failed for #{clean_id}: {e}")
                return {"error": str(e), "sme_id": clean_id}

    async def get_risk_score(sme_id: str) -> Dict[str, Any]:
        """Get the current computed risk score and top risk drivers for an SME.

        Args:
            sme_id: SME ID (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching risk score for SME: #{clean_id}")
        async with httpx.AsyncClient(timeout=30.0) as http:
            try:
                response = await http.get(
                    f"{config.backend_api_url}/api/v1/sme/{clean_id}/risk",
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Risk score fetch failed for #{clean_id}: {e}")
                return {"error": str(e), "sme_id": clean_id}

    return [get_peer_comparison, get_risk_score]


class SMEAnalysisAgent:
    """Performs comprehensive deep-dive analysis of individual SMEs"""

    def __init__(self):
        self.config = get_config()

        # MCPToolset gives the agent direct access to all 24 data_server tools:
        # assess_financial_health, get_revenue_trend, get_liquidity_analysis,
        # get_employee_count, get_recent_departures, assess_news_risk,
        # get_company_info, check_compliance_status, assess_digital_presence,
        # get_payment_health, check_payment_stress_signals, and more.
        mcp_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=self.config.mcp_server_url + "/mcp",
            )
        )

        extra_tools = make_sme_tools(self.config)

        self.agent = Agent(
            name="sme_analysis_agent",
            model=self.config.model_name,
            description="Deep credit risk analysis agent for individual SMEs",
            instruction=SME_SYSTEM_INSTRUCTION,
            tools=[mcp_toolset, *extra_tools],
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="sme_analysis",
            session_service=self.session_service,
        )

        logger.info("SME Analysis Agent initialised")

    async def analyze(self, sme_id: str) -> str:
        """Perform comprehensive analysis of an individual SME.

        Args:
            sme_id: SME ID to analyse (e.g. '#0142')
        """
        import uuid
        clean_id = sme_id.replace("#", "")
        session_id = str(uuid.uuid4())
        logger.info(f"Analysing SME: #{clean_id} [session: {session_id}]")

        try:
            await self.session_service.create_session(
                app_name="sme_analysis",
                user_id="system",
                session_id=session_id,
            )

            prompt = f"""Perform a comprehensive analysis of SME #{clean_id}.

Steps:
1. Call assess_financial_health to get the overall financial picture
2. Call get_revenue_trend and get_liquidity_analysis for deeper financial detail
3. Call get_employee_count and get_recent_departures to review workforce signals
4. Call assess_digital_presence for web and traffic trends
5. Call assess_news_risk for recent news sentiment
6. Call check_compliance_status for regulatory standing
7. Call get_payment_health for payment behaviour
8. Call get_risk_score to get the computed risk score and key drivers
9. Call get_peer_comparison to benchmark against sector peers
10. Summarise findings with specific data points and actionable recommendations
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

            return final_response or "No analysis generated"

        except Exception as e:
            logger.error(f"SME analysis error: {e}", exc_info=True)
            return f"Error analysing SME #{clean_id}: {str(e)}"