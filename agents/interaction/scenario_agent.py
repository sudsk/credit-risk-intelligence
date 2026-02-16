"""
Scenario Simulation Agent
Uses ADK v1.19.0 for portfolio-wide what-if analysis
"""
import logging
import asyncio
from typing import Any, Dict, List

from google import genai
from google.genai.types import Tool, FunctionDeclaration, Schema, Type

from agents.shared.config import get_config
from agents.shared.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class ScenarioAgent:
    """
    Scenario Simulation Agent
    Runs what-if analysis across entire portfolio
    """
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize Gemini client
        self.client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        
        # Initialize MCP client
        self.mcp_client = MCPClient(self.config.mcp_server_url)
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("Scenario Agent initialized")
    
    def _create_agent(self) -> genai.Agent:
        """Create agent with scenario analysis tools"""
        
        tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="identify_affected_smes",
                        description="Identify SMEs affected by a scenario based on parameters",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "scenario_type": Schema(
                                    type=Type.STRING,
                                    description="Type of scenario (interest_rate, regulation, sector_shock, etc.)"
                                ),
                                "parameters": Schema(
                                    type=Type.OBJECT,
                                    description="Scenario parameters (e.g., rate_change: 1.0 for +1%)"
                                ),
                            },
                            required=["scenario_type", "parameters"]
                        )
                    ),
                    FunctionDeclaration(
                        name="calculate_sme_impact",
                        description="Calculate impact of scenario on specific SME",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_id": Schema(
                                    type=Type.STRING,
                                    description="SME ID"
                                ),
                                "scenario_parameters": Schema(
                                    type=Type.OBJECT,
                                    description="Scenario parameters"
                                ),
                            },
                            required=["sme_id", "scenario_parameters"]
                        )
                    ),
                    FunctionDeclaration(
                        name="aggregate_portfolio_impact",
                        description="Aggregate individual SME impacts to portfolio level",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "sme_impacts": Schema(
                                    type=Type.ARRAY,
                                    description="List of individual SME impact results"
                                ),
                            },
                            required=["sme_impacts"]
                        )
                    ),
                ]
            )
        ]
        
        system_instruction = """You are a Scenario Simulation Agent for SME credit risk analysis.

Your role is to:
1. Understand the scenario description and parameters
2. Identify affected SMEs based on scenario type
3. Calculate impact for each affected SME
4. Aggregate results to portfolio level
5. Generate actionable insights

Scenario Types:
- interest_rate: Changes in interest rates affecting variable rate loans
- regulation: Regulatory changes (e.g., product bans, compliance requirements)
- sector_shock: Sector-specific events (e.g., retail downturn, tech bubble)
- economic: Macroeconomic changes (GDP, unemployment, inflation)
- geographic: Regional events affecting specific geographies

Process:
1. Parse scenario description to extract type and parameters
2. Use identify_affected_smes to find relevant SMEs
3. Use calculate_sme_impact for each affected SME
4. Use aggregate_portfolio_impact to generate final results

Provide clear before/after comparisons and identify top impacted SMEs.
"""
        
        agent = self.client.agentic.create_agent(
            model=self.config.model_name,
            system_instruction=system_instruction,
            tools=tools,
        )
    
    async def identify_affected_smes(
        self,
        scenario_type: str,
        parameters: Dict[str, Any]
    ) -> List[str]:
        """Identify SMEs affected by scenario"""
        logger.info(f"Identifying affected SMEs for scenario type: {scenario_type}")
        
        # Call MCP to get filtered SME list
        result = await self.mcp_client.call_tool(
            "bigquery_server",
            "filter_smes_by_criteria",
            {
                "scenario_type": scenario_type,
                "parameters": parameters
            }
        )
        
        # For demo, return mock list based on scenario type
        if scenario_type == "interest_rate":
            # SMEs with variable rate loans
            return ["#0234", "#0456", "#0789", "#0142"]  # Mock: would be ~487 SMEs
        elif scenario_type == "regulation":
            # SMEs affected by regulation
            return ["#0445", "#0672"]  # Mock: Hemp ban affected SMEs
        else:
            # Generic
            return ["#0142", "#0287", "#0531"]
    
    async def calculate_sme_impact(
        self,
        sme_id: str,
        scenario_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate impact on specific SME"""
        logger.info(f"Calculating impact for SME: {sme_id}")
        
        # Get current SME data
        sme_data = await self.mcp_client.call_tool(
            "bigquery_server",
            "get_sme_data",
            {"sme_id": sme_id.replace("#", "")}
        )
        
        # Call Vertex AI model for risk recalculation
        new_score = await self.mcp_client.call_tool(
            "vertex_ai_server",
            "predict_risk_score",
            {
                "sme_id": sme_id.replace("#", ""),
                "scenario_parameters": scenario_parameters
            }
        )
        
        # Mock calculation for demo
        current_score = sme_data.get("risk_score", 65)
        impact = scenario_parameters.get("expected_impact", 10)
        new_score_value = min(100, current_score + impact)
        
        return {
            "sme_id": sme_id,
            "sme_name": sme_data.get("name", "Unknown"),
            "score_before": current_score,
            "score_after": new_score_value,
            "change": new_score_value - current_score,
            "category_before": self._get_category(current_score),
            "category_after": self._get_category(new_score_value),
        }
    
    async def aggregate_portfolio_impact(
        self,
        sme_impacts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate individual impacts to portfolio level"""
        logger.info("Aggregating portfolio impact")
        
        # Calculate before/after counts
        critical_before = sum(1 for s in sme_impacts if s["category_before"] == "critical")
        critical_after = sum(1 for s in sme_impacts if s["category_after"] == "critical")
        
        # Calculate average score changes
        avg_change = sum(s["change"] for s in sme_impacts) / len(sme_impacts) if sme_impacts else 0
        
        # Identify top impacted
        top_impacted = sorted(sme_impacts, key=lambda x: x["change"], reverse=True)[:10]
        
        return {
            "portfolio_impact": {
                "critical_before": critical_before + 23,  # Add base portfolio
                "critical_after": critical_after + 23,
                "avg_score_change": round(avg_change, 1),
                "total_affected": len(sme_impacts)
            },
            "top_impacted": top_impacted,
        }
    
    def _get_category(self, score: int) -> str:
        """Get risk category from score"""
        if score >= 80:
            return "critical"
        elif score >= 50:
            return "medium"
        else:
            return "stable"
    
    async def simulate(self, scenario_description: str) -> Dict[str, Any]:
        """
        Main entry point for scenario simulation
        
        Args:
            scenario_description: Natural language scenario description
            
        Returns:
            Scenario results with portfolio impact
        """
        logger.info(f"Simulating scenario: {scenario_description}")
        
        try:
            # Start agent session
            session = self.agent.start_session()
            
            # Send scenario description
            prompt = f"""Analyze this scenario and run a complete simulation:

Scenario: {scenario_description}

Steps:
1. Identify the scenario type and parameters
2. Find all affected SMEs
3. Calculate impact for each SME
4. Aggregate to portfolio level
5. Return comprehensive results

Portfolio context:
- Total SMEs: 1,284
- Current critical: 23
- Current medium: 142
- Current stable: 1,119
"""
            
            response = session.send_message(prompt)
            
            # Process function calls
            while response.function_calls:
                function_responses = []
                
                for fc in response.function_calls:
                    logger.info(f"Agent calling function: {fc.name}")
                    
                    if fc.name == "identify_affected_smes":
                        result = await self.identify_affected_smes(
                            fc.args.get("scenario_type"),
                            fc.args.get("parameters", {})
                        )
                    elif fc.name == "calculate_sme_impact":
                        result = await self.calculate_sme_impact(
                            fc.args.get("sme_id"),
                            fc.args.get("scenario_parameters", {})
                        )
                    elif fc.name == "aggregate_portfolio_impact":
                        result = await self.aggregate_portfolio_impact(
                            fc.args.get("sme_impacts", [])
                        )
                    else:
                        result = {"error": f"Unknown function: {fc.name}"}
                    
                    function_responses.append({
                        "id": fc.id,
                        "result": result
                    })
                
                response = session.send_message(function_responses)
            
            # Parse final response
            return {
                "description": scenario_description,
                "analysis": response.text,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Scenario simulation error: {e}")
            return {
                "description": scenario_description,
                "error": str(e),
                "status": "failed"
            }
