from dataclasses import dataclass, field
from typing import Annotated

from langgraph.graph.message import add_messages

from ..core.models.amazon_product_details import ChatbotProductView


@dataclass
class State:
    messages: Annotated[list, add_messages]
    last_search: list[ChatbotProductView] | None = field(default=None)
    region: str | None = field(default=None)
