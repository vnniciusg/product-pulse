import asyncio
import json

from ...agent import agent
from ..core.models import ChatRequest


async def stream_generator(request: ChatRequest):
    try:
        messages = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]
        config = {"configurable": {"thread_id": request.thread_id}}

        async for chunk in agent.astream(
            {"messages": messages, "region": request.region},
            config=config,
            stream_mode=request.stream_mode,
        ):
            latest_message = chunk["messages"][-1]

            event_data = {
                "type": "message",
                "content": None,
                "tool_calls": None,
                "role": "assistant",
            }

            if latest_message.content:
                event_data["content"] = latest_message.content
                event_data["type"] = "content"

            if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
                event_data["tool_calls"] = [
                    {"name": tc["name"], "id": tc.get("id"), "args": tc.get("args")}
                    for tc in latest_message.tool_calls
                ]
                event_data["type"] = "tool_call"

            yield f"data: {json.dumps(event_data)}\n\n"

            await asyncio.sleep(0.01)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        error_data = {"type": "error", "error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"
