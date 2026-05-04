from models import MODEL_Y1, YANDEX, MODEL_Q36
from settings import TAVILY_API_KEY
import langchain_core
# model = MODEL_Y1
model = MODEL_Q36
# model = YANDEX

import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model=MODEL_Q36,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
print(result["messages"][-1].content_blocks)