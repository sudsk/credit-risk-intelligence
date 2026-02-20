"""
SME Analysis Agent
Deep dive analysis of individual SME health
"""
import logging
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient
from agents.interaction.prompts import SME_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

def make_sme_tools(mcp_client: MCPClient):
    """Create SME analysis tool functions as plain async functions (ADK requirement)"""

    async def get_financial_metrics(sme_id: str) -> Dict[str, Any]:
        """Get financial metrics for an SME from BigQuery.

        Args:
            sme_id: SME ID to retrieve financials for (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching financial metrics for SME: #{clean_id}")
        return await mcp_client.call_tool(
            "bigquery_server", "get_sme_financials", {"sme_id": clean_id}
        )

    async def get_alternative_data(sme_id: str) -> Dict[str, Any]:
        """Get alternative data signals including LinkedIn headcount and web traffic.

        Args:
            sme_id: SME ID to retrieve alternative data for (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching alternative data for SME: #{clean_id}")

        linkedin = await mcp_client.call_tool(
            "linkedin_server", "get_employee_count", {"sme_id": clean_id}
        )
        web_traffic = await mcp_client.call_tool(
            "google_analytics_server", "get_traffic_metrics", {"sme_id": clean_id}
        )

        return {
            "linkedin": linkedin,
            "web_traffic": web_traffic,
        }

    async def get_risk_drivers(sme_id: str) -> Dict[str, Any]:
        """Get the key risk drivers contributing to the SME's current risk score.

        Args:
            sme_id: SME ID to retrieve risk drivers for (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching risk drivers for SME: #{clean_id}")
        return await mcp_client.call_tool(
            "vertex_ai_server", "get_risk_drivers", {"sme_id": clean_id}
        )

    async def get_peer_comparison(sme_id: str) -> Dict[str, Any]:
        """Compare an SME to peers in the same sector and size band.

        Args:
            sme_id: SME ID to compare (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching peer comparison for SME: #{clean_id}")
        return await mcp_client.call_tool(
            "bigquery_server", "get_peer_comparison", {"sme_id": clean_id}
        )

    return [get_financial_metrics, get_alternative_data, get_risk_drivers, get_peer_comparison]


class SMEAnalysisAgent:
    """Performs comprehensive deep-dive analysis of individual SMEs"""

    def __init__(self):
        self.config = get_config()
        self.mcp_client = MCPClient(self.config.mcp_server_url)

        tools = make_sme_tools(self.mcp_client)

        self.agent = Agent(
            name="sme_analysis_agent",
            model=self.config.model_name,
            description="Deep credit risk analysis agent for individual SMEs",
            instruction=SME_SYSTEM_INSTRUCTION,
            tools=tools,
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="sme_analysis",
            session_service=self.session_service,
        )

        logger.info("SME Analysis Agent initialized")

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
1. Call get_financial_metrics to assess financial health
2. Call get_alternative_data to review LinkedIn and web signals
3. Call get_risk_drivers to identify the top risk contributors
4. Call get_peer_comparison to benchmark against sector peers
5. Summarise findings with specific data points and actionable recommendations
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