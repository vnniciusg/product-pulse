import asyncio
import json
from typing import Any, AsyncGenerator

from loguru import logger

from ...agent import agent
from ..core.models import ChatRequest, ChatResponse
from ...decorators import with_timer


class AgentService:
    @staticmethod
    @with_timer
    async def run_agent(request: ChatRequest) -> dict[str, Any]:
        try:
            response = await agent.ainvoke(
                request.to_langgraph_input(),
                config=request.get_config(),
            )
            return response

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise

    @staticmethod
    @with_timer
    async def stream_agent(request: ChatRequest) -> AsyncGenerator[str, None]:
        final_state: dict[str, Any] | None = None
        try:
            async for event in agent.astream_events(
                input=request.to_langgraph_input(),
                config=request.get_config(),
                stream_mode=request.stream_mode,
                version="v2"
            ):
                event_type = event.get("event")
                data = event.get("data", {})
                chunk = data.get("chunk")

                if (
                    event_type == "on_chat_model_stream"
                    and chunk is not None
                    and getattr(chunk, "content", None)
                ):
                    token = event["data"]["chunk"].content
                    yield f"data: {json.dumps({'type': 'token', 'delta': token})}\n\n"

                if event_type == "on_chain_end":
                    final_state = data.get("output")

                if event_type == "on_graph_state":
                    final_state = data

            if final_state:
                final_response = ChatResponse.build_from_state(state=final_state)
                yield f"data: {json.dumps({'type': 'final_state', 'state': final_response.model_dump()})}\n\n"
            
            yield "data: [DONE]\n\n"
                
        except Exception as e:
            error_data = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"