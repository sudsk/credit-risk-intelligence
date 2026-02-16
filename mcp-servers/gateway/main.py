"""
MCP HTTP Gateway
Exposes CSV-based MCP servers as HTTP JSON-RPC endpoints
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import sys
import importlib.util

app = FastAPI(title="MCP Gateway")

# Load MCP servers
SERVERS = {}

def load_server(name: str, path: str):
    """Load MCP server module"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    SERVERS[name] = module

# Load all servers
load_server("linkedin_server", "../data_sources/linkedin_server.py")
load_server("companies_house_server", "../data_sources/companies_house_server.py")
load_server("companies_house_server", "../data_sources/web_traffic_server.py")
load_server("companies_house_server", "../data_sources/news_server.py")
load_server("companies_house_server", "../data_sources/financial_server.py")

class RPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: int

@app.post("/rpc")
async def rpc_handler(request: RPCRequest):
    """Handle JSON-RPC calls"""
    try:
        server_name, tool_name = request.method.split("/")
        server = SERVERS.get(server_name)
        
        if not server:
            return {"error": f"Server {server_name} not found"}
        
        # Call the tool
        tool_func = getattr(server, tool_name, None)
        if not tool_func:
            return {"error": f"Tool {tool_name} not found"}
        
        result = tool_func(**request.params)
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request.id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"message": str(e)},
            "id": request.id
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)