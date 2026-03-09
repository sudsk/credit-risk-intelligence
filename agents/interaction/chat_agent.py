"""
Chat Agent - Conversational AI Assistant
ADK 1.25.0 with MCPToolset for direct MCP server access
"""
import logging
from datetime import datetime
from typing import Any, Dict

import httpx
import vertexai  
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.interaction.prompts import CHAT_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


def make_chat_tools(config):
    """
    Non-MCP tools for the chat agent.
    MCP tools (analyze_sme data, news) are provided via MCPToolset directly —
    the agent can call get_employee_count, get_recent_departures, get_company_info,
    assess_financial_health, get_recent_events, assess_news_risk, etc. natively.
    """

    async def run_scenario(
        scenario_type: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run a stress test scenario on the SME portfolio.

        Args:
            scenario_type: One of: interest_rate, sector_shock, recession,
                        eba_2025_adverse, geopolitical, climate_transition
            parameters: Dict of scenario parameters e.g.
                        {"rate_change": 50} for interest_rate
                        {"gdp_change": -3.5, "unemployment_change": 3.0} for recession
                        {"sector": "Retail/Fashion", "severity": 0.7} for sector_shock
        """
        logger.info(f"Running scenario: {scenario_type} {parameters}")
        async with httpx.AsyncClient(timeout=60.0) as http:
            try:
                response = await http.post(
                    f"{config.backend_api_url}/api/v1/scenarios/run",
                    json={"scenario_type": scenario_type, "parameters": parameters},
                )
                response.raise_for_status()
                data = response.json()
                return {"job_id": data.get("job_id"), "status": data.get("status")}
            except Exception as e:
                logger.error(f"Scenario creation failed: {e}")
                return {"error": str(e)}

    async def get_portfolio_summary() -> Dict[str, Any]:
        """Get current portfolio-level metrics and risk summary from the backend."""
        logger.info("Fetching portfolio summary")
        async with httpx.AsyncClient(timeout=30.0) as http:
            try:
                response = await http.get(
                    f"{config.backend_api_url}/api/v1/portfolio/summary",
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Portfolio summary failed: {e}")
                return {"error": str(e)}

    return [run_scenario, get_portfolio_summary]


class ChatAgent:
    """Credit Risk Chat Assistant Agent using ADK with MCPToolset"""

    def __init__(self):
        self.config = get_config()

        vertexai.init(
            project=self.config.project_id,
            location=self.config.location,
        )
        logger.info(f"Vertex AI initialised: project={self.config.project_id}, location={self.config.location}")

        # MCPToolset gives the agent direct access to all 24 data_server tools.
        # No MCPClient wrapper needed — ADK handles discovery and invocation.
        mcp_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=self.config.mcp_server_url + "/mcp",
            )
        )

        # Non-MCP tools (backend calls, scenario runner)
        extra_tools = make_chat_tools(self.config)

        self.agent = Agent(
            name="credit_risk_chat_agent",
            model=self.config.model_name,
            description="Credit Risk AI Assistant for SME portfolio analysis",
            instruction=CHAT_SYSTEM_INSTRUCTION,
            tools=[mcp_toolset, *extra_tools],
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="credit_risk_chat",
            session_service=self.session_service,
        )

        logger.info("Chat Agent initialised")

    async def process_query(self, user_query: str, session_id: str = "default") -> str:
        """Process user query using the ADK agent."""
        logger.info(f"Processing query for session {session_id}: {user_query}")

        try:
            try:
                session = await self.session_service.get_session(
                    app_name="credit_risk_chat",
                    user_id="user",
                    session_id=session_id,
                )
            except Exception:
                session = None    

            if session is None:
                await self.session_service.create_session(
                    app_name="credit_risk_chat",
                    user_id="user",
                    session_id=session_id,
                )

            content = Content(parts=[Part(text=user_query)], role="user")
            final_response = None

            async for event in self.runner.run_async(
                user_id="user",
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                    break

            return final_response or "No response generated"

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"