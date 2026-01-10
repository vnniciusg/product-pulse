from typing import Any, TypedDict

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class LangGraphInput(TypedDict):
    messages: list[dict[str, Any]]
    region: str | None


class ChatRequest(BaseModel):
    messages: list[Message]
    region: str | None = Field(default=None)
    thread_id: str | None = Field(default="default")
    stream_mode: list[str] | None = Field(default=["values"])

    def to_langgraph_input(self) -> LangGraphInput:
        return {
            "messages": [msg.model_dump() for msg in self.messages],
            "region": self.region,
        }

    def get_config(self) -> dict[str, Any]:
        return {"configurable": {"thread_id": self.thread_id}}


class ChatResponse(BaseModel):
    content: str
    role: str
    last_search: list[dict[str, Any]] | None = Field(default=None)

    @classmethod
    def build_from_state(cls, state: dict[str, Any]) -> "ChatResponse":
        _last_ai_message = next(
            (msg.content for msg in reversed(state.get("messages", [])) if hasattr(msg, "type") and msg.type == "ai"),
            None
        )

        return cls(
            content=_last_ai_message,
            role="ai",
            last_search=state.get("last_search", None),
        )