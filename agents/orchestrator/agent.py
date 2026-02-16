"""
Master Orchestrator Agent
Routes requests to specialized agents using ADK v1.19.0
"""
import logging
from typing import Any, Dict

from google import genai
from google.genai.types import Tool, FunctionDeclaration, Schema, Type

from agents.shared.config import get_config
from agents.interaction.chat_agent import ChatAgent
from agents.interaction.scenario_agent import ScenarioAgent
from agents.interaction.sme_agent import SMEAnalysisAgent

logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """
    Master Orchestrator Agent
    Routes user requests to appropriate specialized agents
    """
    
    def __init__(self):
        self.config = get_config()
        
        self.client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        
        # Initialize specialized agents
        self.chat_agent = ChatAgent()
        self.scenario_agent = ScenarioAgent()
        self.sme_agent = SMEAnalysisAgent()
        
        # Create orchestrator agent
        self.agent = self._create_agent()
        
        logger.info("Master Orchestrator initialized")
    
    def _create_agent(self) -> genai.Agent:
        """Create orchestrator agent"""
        
        tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="route_to_chat_agent",
                        description="Route general queries and conversations to chat agent",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "query": Schema(type=Type.STRING, description="User query"),
                            },
                            required=["query"]
                        )
                    ),
                    FunctionDeclaration(
                        name="route_to_scenario_agent",
                        description="Route scenario analysis requests to scenario agent",
                        parameters=Schema(
                            type=Type.OBJECT,
                            properties={
                                "scenario_description": Schema(
                                    type=Type.STRING,
                                    description="Scenario description"
                                ),
                            },
                            required=["scenario_description"]
                        )
                    ),
                    FunctionDeclaration(
                        name="route_to_sme_agent",
                        description="Route deep SME analysis requests to SME agent",
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
        
        system_instruction = """You are the Master Orchestrator for SME Credit Risk platform.

Your role is to analyze user requests and route them to the appropriate specialized agent:

1. **Chat Agent** - General queries, portfolio metrics, news intelligence
   - "What's our portfolio status?"
   - "Show me recent alerts"
   - "Who is TechStart Solutions?"

2. **Scenario Agent** - What-if analysis, portfolio simulations
   - "What if interest rates go up 1%?"
   - "How would a hemp ban affect us?"
   - "Simulate GDP drop of 2%"

3. **SME Agent** - Deep dive analysis of specific SME
   - "Analyze TechStart Solutions in detail"
   - "Deep dive on SME #0142"
   - "Full analysis of GreenLeaf Products"

Route based on intent, not just keywords. Consider context and user's goal.
"""
        
        agent = self.client.agentic.create_agent(
            model=self.config.model_name,
            system_instruction=system_instruction,
            tools=tools,
        )
    
    async def route_to_chat_agent(self, query: str) -> str:
        """Route to chat agent"""
        return await self.chat_agent.process_query(query)
    
    async def route_to_scenario_agent(self, scenario_description: str) -> Dict[str, Any]:
        """Route to scenario agent"""
        return await self.scenario_agent.simulate(scenario_description)
    
    async def route_to_sme_agent(self, sme_id: str) -> str:
        """Route to SME agent"""
        return await self.sme_agent.analyze(sme_id)
    
    async def process(self, user_input: str, session_id: str = "default") -> str:
        """
        Process user input and route to appropriate agent
        
        Args:
            user_input: User's request
            session_id: Session ID
            
        Returns:
            Response from specialized agent
        """
        logger.info(f"Orchestrator processing: {user_input}")
        
        try:
            session = self.agent.start_session(session_id=session_id)
            response = session.send_message(user_input)
            
            # Process routing function calls
            while response.function_calls:
                function_responses = []
                
                for fc in response.function_calls:
                    logger.info(f"Routing to: {fc.name}")
                    
                    if fc.name == "route_to_chat_agent":
                        result = await self.route_to_chat_agent(fc.args.get("query"))
                    elif fc.name == "route_to_scenario_agent":
                        result = await self.route_to_scenario_agent(
                            fc.args.get("scenario_description")
                        )
                    elif fc.name == "route_to_sme_agent":
                        result = await self.route_to_sme_agent(fc.args.get("sme_id"))
                    else:
                        result = f"Unknown routing: {fc.name}"
                    
                    function_responses.append({"id": fc.id, "result": result})
                
                response = session.send_message(function_responses)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return f"Error processing request: {str(e)}"
