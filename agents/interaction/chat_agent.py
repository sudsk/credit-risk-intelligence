"""
Chat Agent - Conversational AI Assistant
Using ADK patterns
"""
import logging
from datetime import datetime
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient
from agents.interaction.prompts import CHAT_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


def make_tools(mcp_client: MCPClient, config):
    """Create tool functions as plain async functions (ADK requirement)"""

    async def analyze_sme(sme_id: str) -> Dict[str, Any]:
        """Deep analysis of specific SME health and risk factors using alternative data sources.
        
        Args:
            sme_id: SME ID to analyze (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Analyzing SME: #{clean_id}")

        results = {}
        results["linkedin"] = await mcp_client.call_tool(
            "linkedin_server", "get_employee_count", {"sme_id": clean_id}
        )
        results["recent_departures"] = await mcp_client.call_tool(
            "linkedin_server", "get_recent_departures", {"sme_id": clean_id, "days": 30}
        )
        results["companies_house"] = await mcp_client.call_tool(
            "companies_house_server", "get_company_info", {"sme_id": clean_id}
        )
        results["financial"] = await mcp_client.call_tool(
            "financial_server", "assess_financial_health", {"sme_id": clean_id}
        )

        # Build summary
        summary_parts = []
        if "linkedin" in results and not results["linkedin"].get("error"):
            li = results["linkedin"]
            summary_parts.append(f"Employees: {li.get('employee_count', 'N/A')}, Trend: {li.get('trend', 'N/A')}")
        if "recent_departures" in results and not results["recent_departures"].get("error"):
            deps = results["recent_departures"]
            if isinstance(deps, list) and len(deps) > 0:
                summary_parts.append(f"{len(deps)} departure(s) in last 30 days")
        if "financial" in results and not results["financial"].get("error"):
            fin = results["financial"]
            summary_parts.append(f"Financial Health: {fin.get('health_rating', 'N/A')}, Risk Score: {fin.get('financial_health_score', 'N/A')}")

        return {
            "sme_id": f"#{clean_id}",
            "analysis": results,
            "summary": " | ".join(summary_parts) if summary_parts else "No data available"
        }

    async def run_scenario(description: str) -> Dict[str, Any]:
        """Run what-if scenario analysis on the SME portfolio.
        
        Args:
            description: Scenario description (e.g. 'What if interest rates rise 1%?')
        """
        logger.info(f"Running scenario: {description}")
        import httpx
        async with httpx.AsyncClient() as http:
            try:
                response = await http.post(
                    f"{config.backend_api_url}/api/v1/scenarios",
                    json={"description": description}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Scenario creation failed: {e}")
                return {"error": str(e)}

    async def get_portfolio_metrics() -> Dict[str, Any]:
        """Get current portfolio-level metrics and summary statistics."""
        logger.info("Fetching portfolio metrics")
        return await mcp_client.call_tool(
            "bigquery_server", "get_portfolio_metrics", {}
        )

    async def get_news_intelligence(sme_id: str) -> Dict[str, Any]:
        """Get latest news intelligence and alerts for a specific SME.
        
        Args:
            sme_id: SME ID to get news for (e.g. '0142' or '#0142')
        """
        clean_id = sme_id.replace("#", "")
        logger.info(f"Fetching news for: #{clean_id}")
        return await mcp_client.call_tool(
            "news_server", "get_sme_news", {"sme_id": clean_id}
        )

    return [analyze_sme, run_scenario, get_portfolio_metrics, get_news_intelligence]


async def inject_context(callback_context, **kwargs):
    """Before-agent callback: inject current timestamp into session state each turn."""
    now = datetime.now()
    callback_context.state["current_time"] = now.strftime("%A, %Y-%m-%d %H:%M")
    callback_context.state["analysis_date"] = now.strftime("%Y-%m-%d")


class ChatAgent:
    """Credit Risk Chat Assistant Agent using ADK"""

    def __init__(self):
        self.config = get_config()
        self.mcp_client = MCPClient(self.config.mcp_server_url)

        tools = make_tools(self.mcp_client, self.config)

        self.agent = Agent(
            name="credit_risk_chat_agent",
            model=self.config.model_name,
            description="Credit Risk AI Assistant for SME portfolio analysis",
            instruction=CHAT_SYSTEM_INSTRUCTION,
            tools=tools,
            before_agent_callback=[inject_context],
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="credit_risk_chat",
            session_service=self.session_service,
        )

        logger.info("Chat Agent initialized")

    async def process_query(self, user_query: str, session_id: str = "default") -> str:
        """Process user query using the ADK agent."""
        logger.info(f"Processing query for session {session_id}: {user_query}")

        try:
            # Get or create session
            session = await self.session_service.get_session(
                app_name="credit_risk_chat",
                user_id="user",
                session_id=session_id,
            )
            if session is None:
                await self.session_service.create_session(
                    app_name="credit_risk_chat",
                    user_id="user",
                    session_id=session_id,
                )

            # Run agent and collect final response
            content = Content(parts=[Part(text=user_query)], role="user")
            final_response = None

            async for event in self.runner.run_async(
                user_id="user",
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    break

            return final_response or "No response generated"

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"