"""
Chat Agent - Conversational AI Assistant
Using ADK v1.19.0 patterns from auto-insurance-agent example
"""
import logging
from typing import Any, Dict

from google import genai
from google.genai.types import Tool, FunctionDeclaration, Schema, Type

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient
from agents.interaction.prompts import CHAT_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    Credit Risk Chat Assistant Agent
    Follows ADK v1.19.0 Agent pattern
    """
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize Gemini client with Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        
        # Initialize MCP client
        self.mcp_client = MCPClient(self.config.mcp_server_url)
        
        # Create agent with tools
        self.agent = self._create_agent()

        self.sessions = {}  # Store sessions by ID
        
        logger.info("Chat Agent initialized")
    
    def _create_agent(self) -> genai.Agent:
        """Create agent with tools following ADK v1.19.0 pattern"""
        
        # Define tools for the agent
        tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="analyze_sme",
                        description="Deep analysis of specific SME health and risk factors using alternative data sources",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(
                                    type=Type.STRING,
                                    description="SME ID (e.g., #0142 or just 0142)"
                                ),
                            },
                            required=["sme_id"]
                        )
                    ),
                    FunctionDeclaration(
                        name="run_scenario",
                        description="Run what-if scenario analysis on the portfolio",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "description": Schema(
                                    type=Type.STRING,
                                    description="Scenario description (e.g., 'What if interest rates go up 1%?')"
                                ),
                            },
                            required=["description"]
                        )
                    ),
                    FunctionDeclaration(
                        name="get_portfolio_metrics",
                        description="Get current portfolio metrics and summary statistics",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={}
                        )
                    ),
                    FunctionDeclaration(
                        name="get_news_intelligence",
                        description="Get latest news intelligence and alerts for a specific SME",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(
                                    type=Type.STRING,
                                    description="SME ID to get news for"
                                ),
                            },
                            required=["sme_id"]
                        )
                    ),
                ]
            )
        ]
        
        # Create and return agent
        agent = self.client.agentic.create_agent(
            model=self.config.model_name,
            system_instruction=CHAT_SYSTEM_INSTRUCTION,
            tools=tools,
        )
        
        return agent
    
    async def analyze_sme(self, sme_id: str) -> Dict[str, Any]:
        """
        Analyze SME using MCP tools
        This is the implementation of the analyze_sme tool
        """
        # Normalize SME ID
        if not sme_id.startswith("#"):
            sme_id = f"#{sme_id}"
        
        logger.info(f"Analyzing SME: {sme_id}")
        
        # Gather data from multiple MCP sources
        results = {}
        
        # LinkedIn data
        linkedin_data = await self.mcp_client.call_tool(
            "linkedin_server",
            "get_employee_count",
            {"sme_id": sme_id.replace("#", "")}
        )
        results["linkedin"] = linkedin_data
        
        # Recent departures
        departures = await self.mcp_client.call_tool(
            "linkedin_server",
            "get_recent_departures",
            {"sme_id": sme_id.replace("#", ""), "days": 30}
        )
        results["recent_departures"] = departures
        
        # Companies House data
        company_info = await self.mcp_client.call_tool(
            "companies_house_server",
            "get_company_info",
            {"sme_id": sme_id.replace("#", "")}
        )
        results["companies_house"] = company_info
        
        # BigQuery - SME metrics
        sme_data = await self.mcp_client.call_tool(
            "bigquery_server",
            "get_sme_data",
            {"sme_id": sme_id.replace("#", "")}
        )
        results["sme_data"] = sme_data
        
        return {
            "sme_id": sme_id,
            "analysis": results,
            "summary": self._summarize_sme_analysis(results)
        }
    
    async def run_scenario(self, description: str) -> Dict[str, Any]:
        """
        Run scenario simulation
        This is the implementation of the run_scenario tool
        """
        logger.info(f"Running scenario: {description}")
        
        # Call scenario simulation via backend API
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.config.backend_api_url}/api/v1/scenarios",
                    json={"description": description}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Scenario creation failed: {e}")
                return {"error": str(e)}
    
    async def get_portfolio_metrics(self) -> Dict[str, Any]:
        """
        Get portfolio metrics
        This is the implementation of the get_portfolio_metrics tool
        """
        logger.info("Fetching portfolio metrics")
        
        metrics = await self.mcp_client.call_tool(
            "bigquery_server",
            "get_portfolio_metrics",
            {}
        )
        
        return metrics
    
    async def get_news_intelligence(self, sme_id: str) -> Dict[str, Any]:
        """
        Get news intelligence for SME
        This is the implementation of the get_news_intelligence tool
        """
        logger.info(f"Fetching news intelligence for: {sme_id}")
        
        news = await self.mcp_client.call_tool(
            "news_intelligence_server",
            "get_sme_news",
            {"sme_id": sme_id.replace("#", "")}
        )
        
        return news
    
    def _summarize_sme_analysis(self, results: Dict[str, Any]) -> str:
        """Summarize SME analysis results"""
        summary_parts = []
        
        # LinkedIn summary
        if "linkedin" in results and not results["linkedin"].get("error"):
            linkedin = results["linkedin"]
            summary_parts.append(
                f"Employee count: {linkedin.get('employee_count', 'N/A')}, "
                f"Trend: {linkedin.get('trend', 'N/A')}"
            )
        
        # Departures
        if "recent_departures" in results and not results["recent_departures"].get("error"):
            departures = results["recent_departures"]
            if isinstance(departures, list) and len(departures) > 0:
                summary_parts.append(
                    f"{len(departures)} employee departure(s) in last 30 days"
                )
        
        # SME data
        if "sme_data" in results and not results["sme_data"].get("error"):
            sme = results["sme_data"]
            summary_parts.append(
                f"Risk Score: {sme.get('risk_score', 'N/A')}, "
                f"Category: {sme.get('risk_category', 'N/A')}"
            )
        
        return " | ".join(summary_parts) if summary_parts else "No data available"
    
    async def process_query(self, user_query: str, session_id: str = "default") -> str:
        """
        Process user query using the agent
        
        Args:
            user_query: User's question
            session_id: Session ID for conversation history
            
        Returns:
            Agent's response
        """
        logger.info(f"Processing query: {user_query}")

        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = self.agent.start_session(session_id=session_id)
        
        session = self.sessions[session_id]
        
        try:
            # Start agent session
            session = self.agent.start_session(session_id=session_id)
            
            # Send user query
            response = session.send_message(user_query)
            
            # Process any function calls
            while response.function_calls:
                function_responses = []
                
                for fc in response.function_calls:
                    logger.info(f"Agent calling function: {fc.name}")
                    
                    # Execute the function
                    if fc.name == "analyze_sme":
                        result = await self.analyze_sme(fc.args.get("sme_id"))
                    elif fc.name == "run_scenario":
                        result = await self.run_scenario(fc.args.get("description"))
                    elif fc.name == "get_portfolio_metrics":
                        result = await self.get_portfolio_metrics()
                    elif fc.name == "get_news_intelligence":
                        result = await self.get_news_intelligence(fc.args.get("sme_id"))
                    else:
                        result = {"error": f"Unknown function: {fc.name}"}
                    
                    function_responses.append({
                        "id": fc.id,
                        "result": result
                    })
                
                # Send function results back to agent
                response = session.send_message(function_responses)
            
            # Return final text response
            return response.text
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
