from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, ToolCallLimitMiddleware
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from .prompts import SYSTEM_PROMPT
from .state import State
from .tools.search_on_amazon import search_on_amazon

load_dotenv()

agent = create_agent(
    model=init_chat_model("gpt-5.2"),
    system_prompt=SYSTEM_PROMPT,
    tools=[search_on_amazon],
    state_schema=State,
    checkpointer=InMemorySaver(),
    middleware=[
        ToolCallLimitMiddleware(tool_name="search_on_amazon", run_limit=3),
        SummarizationMiddleware(
            model="gpt-5-mini", trigger=("tokens", 2048)
        ),
    ],
)
