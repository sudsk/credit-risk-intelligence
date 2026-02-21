"""
Shared configuration for all agents
ADK 1.25.0
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Agent configuration"""
    project_id: str
    location: str
    model_name: str = "gemini-2.5-flash"
    mcp_server_url: str = "http://localhost:8001"
    backend_api_url: str = "http://localhost:8000"


def get_config() -> Config:
    """Load configuration from environment"""
    return Config(
        project_id=os.getenv("GCP_PROJECT_ID", "main-nova-470907-h8"),
        location=os.getenv("VERTEX_AI_LOCATION", "europe-west2"),
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8001"),
        backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8000"),
    )