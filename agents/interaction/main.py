"""
FastAPI server for Chat Agent
Following ADK v1.19.0 patterns
"""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.interaction.chat_agent import ChatAgent
from agents.shared.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Chat Agent API")

# Initialize agent
config = get_config()
chat_agent = ChatAgent()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message"""
    try:
        response_text = await chat_agent.process_query(
            request.message,
            request.session_id
        )
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
