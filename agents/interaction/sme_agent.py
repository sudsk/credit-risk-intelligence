"""
SME Analysis Agent
Deep dive analysis of individual SME health
"""
import logging
from typing import Any, Dict

from google import genai
from google.genai.types import Tool, FunctionDeclaration, Schema, Type

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class SMEAnalysisAgent:
    """
    SME Analysis Agent
    Performs comprehensive analysis of individual SME
    """
    
    def __init__(self):
        self.config = get_config()
        
        self.client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        
        self.mcp_client = MCPClient(self.config.mcp_server_url)
        self.agent = self._create_agent()
        
        logger.info("SME Analysis Agent initialized")
    
    def _create_agent(self) -> genai.Agent:
        """Create SME analysis agent"""
        
        tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="get_financial_metrics",
                        description="Get financial metrics for SME from BigQuery",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(type=Type.STRING, description="SME ID"),
                            },
                            required=["sme_id"]
                        )
                    ),
                    FunctionDeclaration(
                        name="get_alternative_data",
                        description="Get alternative data signals (LinkedIn, web traffic, reviews)",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(type=Type.STRING, description="SME ID"),
                            },
                            required=["sme_id"]
                        )
                    ),
                    FunctionDeclaration(
                        name="get_risk_drivers",
                        description="Get key risk drivers contributing to current risk score",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(type=Type.STRING, description="SME ID"),
                            },
                            required=["sme_id"]
                        )
                    ),
                    FunctionDeclaration(
                        name="get_peer_comparison",
                        description="Compare SME to peers in same sector and size",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(type=Type.STRING, description="SME ID"),
                            },
                            required=["sme_id"]
                        )
                    ),
                ]
            )
        ]
        
        system_instruction = """You are an SME Analysis Agent specializing in deep credit risk assessment.

Your role:
1. Gather comprehensive data from multiple sources
2. Identify key risk drivers and trends
3. Compare SME to industry peers
4. Generate actionable recommendations

Analysis Framework:
1. Financial Health
   - Revenue trends (QoQ, YoY)
   - Profitability (EBITDA, margins)
   - Debt service coverage
   - Cash reserves

2. Alternative Data Signals
   - Employee changes (LinkedIn)
   - Web traffic trends
   - Customer sentiment (reviews)
   - Payment behavior

3. External Factors
   - Sector health
   - Geographic risks
   - Regulatory compliance
   - Competition

4. Risk Drivers
   - Top 3-5 factors contributing to risk score
   - Recent changes and trends
   - Forward-looking indicators

Provide clear, actionable insights with specific data points and recommendations.
"""
        
        return self.client.adk.agents.create(
            model=self.config.model_name,
            system_instruction=system_instruction,
            tools=tools,
        )
    
    async def get_financial_metrics(self, sme_id: str) -> Dict[str, Any]:
        """Get financial metrics"""
        return await self.mcp_client.call_tool(
            "bigquery_server",
            "get_sme_financials",
            {"sme_id": sme_id.replace("#", "")}
        )
    
    async def get_alternative_data(self, sme_id: str) -> Dict[str, Any]:
        """Get alternative data signals"""
        # LinkedIn data
        linkedin = await self.mcp_client.call_tool(
            "linkedin_server",
            "get_employee_count",
            {"sme_id": sme_id.replace("#", "")}
        )
        
        # Web analytics
        web_traffic = await self.mcp_client.call_tool(
            "google_analytics_server",
            "get_traffic_metrics",
            {"sme_id": sme_id.replace("#", "")}
        )
        
        return {
            "linkedin": linkedin,
            "web_traffic": web_traffic,
        }
    
    async def get_risk_drivers(self, sme_id: str) -> Dict[str, Any]:
        """Get risk drivers"""
        return await self.mcp_client.call_tool(
            "vertex_ai_server",
            "get_risk_drivers",
            {"sme_id": sme_id.replace("#", "")}
        )
    
    async def get_peer_comparison(self, sme_id: str) -> Dict[str, Any]:
        """Get peer comparison"""
        return await self.mcp_client.call_tool(
            "bigquery_server",
            "get_peer_comparison",
            {"sme_id": sme_id.replace("#", "")}
        )
    
    async def analyze(self, sme_id: str) -> str:
        """
        Analyze SME comprehensively
        
        Args:
            sme_id: SME ID to analyze
            
        Returns:
            Comprehensive analysis text
        """
        logger.info(f"Analyzing SME: {sme_id}")
        
        try:
            session = self.agent.start_session()
            
            prompt = f"""Perform comprehensive analysis of SME {sme_id}.

Include:
1. Current financial health
2. Alternative data signals
3. Key risk drivers
4. Peer comparison
5. Recommendations

Be specific with data points and actionable.
"""
            
            response = session.send_message(prompt)
            
            # Process function calls
            while response.function_calls:
                function_responses = []
                
                for fc in response.function_calls:
                    if fc.name == "get_financial_metrics":
                        result = await self.get_financial_metrics(fc.args.get("sme_id"))
                    elif fc.name == "get_alternative_data":
                        result = await self.get_alternative_data(fc.args.get("sme_id"))
                    elif fc.name == "get_risk_drivers":
                        result = await self.get_risk_drivers(fc.args.get("sme_id"))
                    elif fc.name == "get_peer_comparison":
                        result = await self.get_peer_comparison(fc.args.get("sme_id"))
                    else:
                        result = {"error": f"Unknown function: {fc.name}"}
                    
                    function_responses.append({"id": fc.id, "result": result})
                
                response = session.send_message(function_responses)
            
            return response.text
            
        except Exception as e:
            logger.error(f"SME analysis error: {e}")
            return f"Error analyzing SME: {str(e)}"
