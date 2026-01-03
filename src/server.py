from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .api.core.models import ChatRequest
from .api.middleware.bearer_auth_middleware import BearerAuthMiddleware
from .api.services.stream_generator import stream_generator
from .core.config import app_config

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
    return StreamingResponse(
        stream_generator(request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/ping")
def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "pong"})
