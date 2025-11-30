"""
MCP Client for fetching data from MCP servers
"""
import httpx
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for calling MCP servers"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call MCP tool"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.server_url}/rpc",
                    json={
                        "jsonrpc": "2.0",
                        "method": f"{server_name}/{tool_name}",
                        "params": params,
                        "id": 1
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", {})
            except Exception as e:
                logger.error(f"MCP call failed: {e}")
                return {"error": str(e)}
