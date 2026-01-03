from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    thread_id: str | None = Field(default="default")
    stream_mode: str | None = Field(default="values")


class ChatResponse(BaseModel):
    content: str
    role: str
    tool_calls: list[dict[str, Any]] | None = Field(default=None)
