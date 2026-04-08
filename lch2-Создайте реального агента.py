from models import MODEL_Y1

# model = MODEL_Y1

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy


# Define system prompt
SYSTEM_PROMPT = """Вы — опытный синоптик.
У вас есть доступ к двум инструментам:
- get_weather_for_location: используйте его, чтобы узнать погоду в конкретном месте.
- get_user_location: используйте его, чтобы узнать местоположение пользователя.
Если пользователь спрашивает вас о погоде, убедитесь, что вы знаете, где он находится.  Если по вопросу можно понять, что пользователь имеет в виду свое местоположение, используйте инструмент get_user_location, чтобы узнать его."""

# Define context schema
@dataclass
class Context:
    """Пользовательская схема контекста среды выполнения."""
    user_id: str

# Define tools
@tool
def get_weather_for_location(city: str) -> str:
    """Сообщает о погоде в указанном городе."""
    return f"Сейчас в {city} солнечно!"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Получение информации о местонахождении пользователе"""
    user_id = runtime.context.user_id
    return "Москва" if user_id == "1" else "Санкт-Питербург"

# Configure model
model = MODEL_Y1
# model = init_chat_model(
#     "claude-sonnet-4-6",
#     temperature=0
# )

# Define response format
@dataclass
class ResponseFormat:
    """Схема ответа для агента."""
    punny_response: str
    weather_conditions: str | None = None

# Set up memory
checkpointer = InMemorySaver()

# Create agent
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)


config = {"configurable": {"thread_id": "1"}}

# response = agent.invoke(
#     {"messages": [{"role": "user", "content": "Какая сегодня погода на улице?"}]},
#     config=config,
#     context=Context(user_id="1")
# )
# print(response['structured_response'])

# response = agent.invoke(
#     {"messages": [{"role": "user", "content": "А какая будет погода завтра?"}]},
#     config=config,
#     context=Context(user_id="1")
# )
# print(response['structured_response'])

while True:
    user_input = input("Напишите свой вопрос (пустая строка для выхода):")
    if user_input == "":
        break
    # Здесь можно обработать введённую строку
    response = agent.invoke(
        {"messages": [{"role": "user", "content": f"user_input"}]},
        config=config,
        context=Context(user_id="1")
    )
    print(response['structured_response'])