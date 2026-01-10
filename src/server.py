from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .api.core.models import ChatRequest, ChatResponse
from .api.middleware.bearer_auth_middleware import BearerAuthMiddleware
from .api.services.agent_service import AgentService
from .core.config import app_config

load_dotenv()

app = FastAPI(
    title=app_config.SERVER.TITLE,
    description=app_config.SERVER.DESCRIPTION,
    version=app_config.SERVER.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[app_config.SERVER.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    BearerAuthMiddleware, excluded_paths=["/docs", "/redoc", "/openapi.json", "/ping"]
)


@app.post("/api/v1/agent/stream")
async def stream_agent(request: ChatRequest):
    """
    Streaming endpoint using Server-Sent Events (SSE).
    
    Example usage with curl:
    curl -N -X POST http://localhost:8000/api/v1/agent/stream \
         -H "Content-Type: application/json" \
         -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
    """
    request.stream_mode = ["messages", "state"]
    return StreamingResponse(
        AgentService.stream_agent(request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.post("/api/v1/agent/run")
async def run_agent(request: ChatRequest): 
    """
    Run the agent and return the response.

    Example usage with curl:
    curl -X POST http://localhost:8000/api/v1/agent/run \
         -H "Content-Type: application/json" \
         -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
    """
    try:
        state = await AgentService.run_agent(request=request)
        response = ChatResponse.build_from_state(state=state)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@app.get("/ping")
def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "pong"})
