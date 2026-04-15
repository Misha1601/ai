# Кратковременная память

## Обзор

Память — это система, которая запоминает информацию о предыдущих взаимодействиях.  Для агентов с искусственным интеллектом память имеет решающее значение, поскольку она позволяет им запоминать предыдущие взаимодействия, учиться на основе обратной связи и адаптироваться к предпочтениям пользователей. Поскольку агенты решают все более сложные задачи с многочисленными взаимодействиями с пользователем, эта возможность становится необходимой как для эффективности, так и для удовлетворения потребностей пользователей.

Кратковременная память позволяет вашему приложению запоминать предыдущие взаимодействия в рамках одного потока или беседы.

<Note>

Поток организует множество взаимодействий в сеансе, подобно тому, как электронная почта группирует сообщения в рамках одного разговора.
</Note>

История разговоров - наиболее распространенная форма кратковременной памяти. Длинные диалоги представляют собой сложную задачу для современных больших языковых моделей: полная история диалога может не уместиться в контекстном окне модели, что приведет к потере контекста или ошибкам.

Даже если ваша модель поддерживает полную длину контекста, большинство больших языковых моделей плохо справляются с длинными контекстами. Они «отвлекаются» на устаревший или не относящийся к теме контент, из-за чего время отклика увеличивается, а затраты возрастают.

Чат-боты принимают контекст в виде [сообщений](/oss/python/langchain/messages), которые включают в себя инструкции (системные сообщения) и вводимые данные (сообщения от пользователей). В чат-приложениях сообщения чередуются между вводимыми пользователем данными и ответами модели, в результате чего список сообщений со временем становится все длиннее. Поскольку контекстные окна ограничены, многие приложения могут извлечь выгоду из использования методов удаления или "забвения" устаревшей информации.

<Tip>

Необходимо запоминать информацию из разговоров? Используйте long-term memory ([долговременную память](/oss/python/langchain/long-term-memory)) для хранения и вызова пользовательских данных или данных уровня приложения в разных потоках и сеансах.
</Tip>

## Использование

Чтобы добавить в агент краткосрочную память (сохранение данных на уровне потока), при создании агента необходимо указать `checkpointer`.

<Info>

    Агент LangChain управляет краткосрочной памятью как частью состояния вашего агента.

    Сохраняя их в состоянии графа, агент может получить доступ ко всему контексту текущего диалога, сохраняя при этом разделение между различными потоками.

    Состояние сохраняется в базе данных (или в памяти) с помощью контрольных указателей, что позволяет возобновить работу потока в любой момент.

    Кратковременная память обновляется при вызове агента или завершении шага (например, вызова инструмента), а состояние считывается в начале каждого шага.
</Info>

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver # [!code highlight]


agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    checkpointer=InMemorySaver(), # [!code highlight]
)

agent.invoke(
    {"messages": [{"role": "user", "content": "Привет! Меня зовут Боб."}]},
    {"настраиваемый": {"thread_id": "1"}}, # [!code highlight]
)
```

### В продакшене

В продакшене используйте чекпоинтер, подключенный к базе данных:

```shell theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
pip install langgraph-checkpoint-postgres
```

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
из langchain.agents импортируем create_agent
из langgraph.checkpoint.postgres импортируем PostgresSaver # [!code highlight]


DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup() # автоматическое создание таблиц в PostgreSQL
    agent = create_agent(
        "gpt-5",
        tools=[get_user_info],
        checkpointer=checkpointer, # [!code highlight]
    )
```

<Примечание>
 Дополнительные варианты контрольных указателей, включая SQLite, Postgres и Azure Cosmos DB, см. в [списке библиотек контрольных указателей](/oss/python/langgraph/persistence#checkpointer-libraries) в документации по персистентности.
</Примечание>

## Настройка памяти агента

По умолчанию агенты используют [`AgentState`](https://reference.langchain.com/python/langchain/agents/middleware/types/AgentState) для управления краткосрочной памятью, в частности историей диалогов с помощью ключа `messages`.

Вы можете расширить [`AgentState`](https://reference.langchain.com/python/langchain/agents/middleware/types/AgentState), добавив дополнительные поля. Пользовательские схемы состояний передаются в [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) с помощью параметра [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema).

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver


class CustomAgentState(AgentState): # [!code highlight]
    user_id: str # [!code highlight]
    preferences: dict # [!code highlight]

agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    state_schema=CustomAgentState, # [!code highlight]
    checkpointer=InMemorySaver(),
)

# Пользовательское состояние можно передать при вызове
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Привет"}],
        "user_id": "user_123", # [!code highlight]
        "preferences": {"theme": "dark"} # [!code highlight]
    },
    {"настраиваемый": {"thread_id": "1"}})
```

## Общие закономерности

При включенном [использование кратковременной памяти] (#) длительные разговоры могут превышать контекстное окно LLM. Распространенными решениями являются:

<CardGroup cols={2}>
 <Заголовок карточки=Значок "Обрезать сообщения" ="ножницы" href=стрелка "#обрезать сообщения">
 Удалите первое или последние N сообщений (перед вызовом LLM)
 </Карточка>

 <Заголовок карточки= Значок "Удалить сообщения"="корзина" href =стрелка "#удалить-сообщения">
 Удалить сообщения из состояния LangGraph навсегда
 </Card>

 <Card title="Свести сообщения в сводку" icon="stack-2" href="#summarize-messages" arrow>
 Сведите в сводку предыдущие сообщения в истории и замените их кратким изложением
 </Card>

 <Card title="Пользовательские стратегии" icon="adjustments">
 Пользовательские стратегии (например, фильтрация сообщений и т.д.)
 </Card>
</CardGroup>

Это позволяет агенту отслеживать разговор, не выходя за рамки контекстного окна LLM.

### Обрезать сообщения.

Большинство LLM имеют максимально поддерживаемое контекстное окно (выраженное в токенах).

Один из способов определить, когда следует обрезать сообщения, — подсчитать количество токенов в истории сообщений и обрезать их, когда их количество приблизится к этому пределу.  Если вы используете LangChain, вы можете воспользоваться утилитой для обрезки сообщений и указать количество токенов, которые нужно оставить в списке, а также `стратегию` (например, оставить последние `max_tokens`) для определения границы.

Чтобы обрезать историю сообщений в агенте, используйте декоратор промежуточного программного обеспечения [`@before_model`](https://reference.langchain.com/python/langchain/agents/middleware/types/before_model):

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from typing import Any


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Сохраняйте только последние несколько сообщений, чтобы они помещались в контекстном окне."""
    messages = state["messages"]

    if len(messages) <= 3:
        return None # Никаких изменений не требуется

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }

agent = create_agent(
    your_model_here,
    tools=your_tools_here,
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": "привет, меня зовут Боб"}, config)
agent.invoke({"messages": "напиши короткое стихотворение о кошках"}, config)
agent.invoke({"messages": "а теперь то же самое, но о собаках"}, config)
final_response = agent.invoke({"messages": "как меня зовут?"}, config)

final_response["messages"][-1].pretty_print()
"""
================================== Сообщение от искусственного интеллекта ==================================

Вас зовут Боб. Вы уже говорили мне об этом.
Если вы хотите, чтобы я называл вас по прозвищу или как-то иначе, просто скажите.
"""
```

### Удалить сообщения

Вы можете удалять сообщения из состояния графа, чтобы управлять историей переписки.

Это полезно, когда вы хотите удалить определенные сообщения или очистить всю историю сообщений.

Чтобы удалить сообщения из состояния графика, вы можете использовать "Удалить сообщение".

Чтобы `RemoveMessage` заработал, вам нужно использовать ключ состояния с [`add_messages`](https://reference.langchain.com/python/langgraph/graph/message/add_messages ) [редуктор](/oss/python/langgraph/graph-api#редукторы).

По умолчанию это обеспечивает [`AgentState`](https://reference.langchain.com/python/langchain/agents/middleware/types/AgentState).

Чтобы удалить определенные сообщения:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import RemoveMessage  # [!code highlight]

def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        # удалить два самых ранних сообщения
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}  # [!code highlight]
```

Чтобы удалить ** все ** сообщения:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langgraph.graph.message import REMOVE_ALL_MESSAGES  # [!code highlight]

def delete_messages(state):
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}  # [!code highlight]
```

<Предупреждение>
 При удалении сообщений **убедитесь**, что итоговая история сообщений корректна. Ознакомьтесь с ограничениями используемого вами поставщика больших языковых моделей. Например:

 * Некоторые поставщики ожидают, что история сообщений начинается с сообщения от пользователя
 * Большинство провайдеров требуют, чтобы за сообщениями `assistant` с вызовами инструментов следовали соответствующие сообщения с результатами работы инструментов.
</Предупреждение>

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import RemoveMessage
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig


@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Удаляйте старые сообщения, чтобы поддерживать порядок в переписке."""
    messages = state["messages"]
    if len(messages) > 2:
        # удаляем два самых старых сообщения
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None


agent = create_agent(
    "gpt-5-nano",
    tools=[],
    system_prompt="Пожалуйста, отвечайте кратко и по существу.",
    middleware=[delete_old_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": "hi! I'm bob"}]},
    config,
    stream_mode="values",
):
    print([(message.type, message.content) for message in event["messages"]])

for event in agent.stream(
    {"сообщения": [{"роль": "пользователь", "содержимое": "как меня зовут?"}]},
    config,
    stream_mode="значения",
):
    print([(message.type, message.content) для сообщения в событии["messages"]])
```

```
[("человек", "привет! Я — Боб")]
[('человек', "привет! Я — Боб"), ('искусственный интеллект', 'Привет, Боб! Рад знакомству. Чем я могу вам помочь сегодня? Я могу отвечать на вопросы, генерировать идеи, писать тексты, объяснять что-то или помогать с кодом.')]
[('человек', "привет! Меня зовут Боб"), ('ai', 'Привет, Боб! Рад знакомству. Чем я могу тебе помочь сегодня? Я могу отвечать на вопросы, генерировать идеи, писать тексты, объяснять что-то или помогать с кодом.'), ('human', "Как меня зовут?")]
[('человек', "привет! я Боб"), ('ai', 'Привет, Боб! Рад знакомству. Чем я могу тебе помочь сегодня? Я могу отвечать на вопросы, генерировать идеи, писать тексты, объяснять что-то или помогать с кодом.'), ('человек', "как меня зовут?"), ('ai', 'Тебя зовут Боб. Чем я могу помочь тебе сегодня, Боб?")]
[("человек", "как меня зовут?"), ("ай", "Тебя зовут Боб. Чем я могу помочь тебе сегодня, Боб?")]
```

### Обобщение сообщений

Проблема с обрезкой или удалением сообщений, как показано выше, заключается в том, что вы можете потерять информацию при отбраковке очереди сообщений.
По этой причине в некоторых приложениях используется более сложный подход к обобщению истории сообщений с помощью модели чата.

<img src="https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/summary.png?fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=c8ed3facdccd4ef5c7e52902c72ba938 " alt="Сводка" width="609" height="242" data-path="oss/изображения/сводка.png" />

Чтобы обобщить историю сообщений в агенте, используйте встроенное промежуточное ПО [`SummarizationMiddleware`](/oss/python/langchain/middleware#summarization):

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig


checkpointer = InMemorySaver()

agent = create_agent(
    model="gpt-4.1",
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4.1-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20)
        )
    ],
    checkpointer=checkpointer,
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": "привет, меня зовут Боб"}, config)
agent.invoke({"messages": "напиши короткое стихотворение о кошках"}, config)
agent.invoke({"messages": "а теперь сделай то же самое, но про собак"}, config)
final_response = agent.invoke({"messages": "как меня зовут?"}, config)

final_response["messages"][-1].pretty_print()
"""
================================== Сообщение от ИИ ==================================

Вас зовут Боб!
"""
```

Смотрите [`SummarizationMiddleware`](/oss /python /langchain / промежуточное программное обеспечение#summarization) для получения дополнительных параметров конфигурации.

## Доступ к памяти

Вы можете получить доступ к краткосрочной памяти (состоянию) агента и изменять ее несколькими способами:

### Инструменты

#### Чтение кратковременной памяти в инструменте

Доступ к кратковременной памяти (состоянию) в инструменте осуществляется с помощью параметра `runtime` (тип `ToolRuntime`).

Параметр `runtime` скрыт в сигнатуре инструмента (поэтому модель его не видит), но инструмент может получать доступ к состоянию через него.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime


class CustomState(AgentState):
 user_id: str

@tool
def get_user_info(
    runtime: ToolRuntime
) -> str:
    """Посмотреть информацию о пользователе."""
    user_id = runtime.state["user_id"]
    return "Пользователь — Джон Смит" if user_id == "user_123" else "Неизвестный пользователь"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_user_info],
    state_schema=CustomState,
)

result = agent.invoke({
    "messages": "look up user information",
    "user_id": "user_123"
})
print(result["messages"][-1].content)
# > Пользователь - Джон Смит.
```

#### Запись в краткосрочную память из инструментов

Чтобы изменить краткосрочную память (состояние) агента во время выполнения, вы можете возвращать обновления состояния непосредственно из инструментов.

Это удобно для сохранения промежуточных результатов или обеспечения доступа к информации для последующих инструментов или подсказок.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command
from pydantic import BaseModel


class CustomState(AgentState): # [!выделение кода]
    user_name: str

class CustomContext(BaseModel):
    user_id: str

@tool
def update_user_info(
    runtime: ToolRuntime[CustomContext, CustomState],
) -> Command:
    """Найдите и обновите информацию о пользователе."""
    user_id = runtime.context.user_id
    name = "Джон Смит" if user_id == "user_123" else "Неизвестный пользователь"
    return Command(update={ # [!выделение кода]
        "user_name": name,
        # обновить историю сообщений
        "messages": [
            ToolMessage(
                "Информация о пользователе успешно получена",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

@tool
def greet(
    runtime: ToolRuntime[CustomContext, CustomState]
) -> str | Command:
    """Используйте это, чтобы поприветствовать пользователя после того, как вы узнали его данные."""
    user_name = runtime.state.get("user_name", None)
    if user_name is None:
        return Command(update={
            "messages": [
                ToolMessage(
                    "Пожалуйста, вызовите инструмент 'update_user_info', он получит и обновит имя пользователя.",
                    tool_call_id=runtime.tool_call_id
                )
            ]
        })
    return f"Привет, {user_name}!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[update_user_info, greet],
    state_schema=CustomState, # [!выделение кода]
    context_schema=CustomContext,
)

agent.invoke(
    {"сообщения": [{"роль": "пользователь", "содержимое": "поприветствуйте пользователя"}]},
    context=CustomContext(user_id="user_123"),
)
```

### Запрос

Получите доступ к кратковременной памяти (state) в промежуточном программном обеспечении для создания динамических запросов на основе истории разговоров или пользовательских полей состояния.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest


class CustomContext(TypedDict):
    user_name: str


def get_weather(city: str) -> str:
    """Узнайте погоду в городе."""
    return f"В {city} всегда солнечно!"


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context["user_name"]
    system_prompt = f"Вы полезный помощник. Обращайтесь к пользователю как {имя_пользователя}".
    return  system_prompt


агент = create_agent(
    модель="gpt-5-nano",
    инструменты=[get_weather],
    промежуточное программное обеспечение =[dynamic_system_prompt],
    context_schema=пользовательский контекст,
)

результат = агент.вызвать(
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    context=CustomContext(user_name="Джон Смит"),
)
for msg in result["messages"]:
    msg.pretty_print()

```

```shell title="Вывод" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
================================ Сообщение от человека =================================

Какая погода в Сан-Франциско?
================================== Сообщение от искусственного интеллекта ==================================
Вызовы инструментов:
    get_weather (call_WFQlOGn4b2yoJrv7cih342FG)
 Идентификатор вызова: call_WFQlOGn4b2yoJrv7cih342FG
    Аргументы:
        город: Сан-Франциско
================================= Сообщение от инструмента =================================
Название: get_weather
В Сан-Франциско всегда солнечно!
================================== Сообщение от искусственного интеллекта ==================================

Привет, Джон Смит, в Сан-Франциско всегда солнечно!
```

### До создания модели

Доступ к кратковременной памяти (состоянию) в промежуточном программном обеспечении [`@before_model`](https://reference.langchain.com/python/langchain/agents/middleware/types/before_model) для обработки сообщений перед вызовами модели.


```mermaid theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
%%{
    init: {
        "fontFamily": "monospace",
        "flowchart": {
        "curve": "basis"
        }
    }
}%%
graph TD
    S(["\_\_start\_\_"])
    PRE(before_model)
    MODEL(model)
    TOOLS(tools)
    END(["\_\_end\_\_"])
    S --> PRE
    PRE --> MODEL
    MODEL -.-> TOOLS
    MODEL -.-> END
    TOOLS --> PRE
    classDef blueHighlight fill:#DBEAFE,stroke:#2563EB,color:#1E3A8A;
    classDef neutral fill:#F3F4F6,stroke:#9CA3AF,stroke-width:2px,color:#374151;
    class S blueHighlight;
    class END blueHighlight;
    class PRE,MODEL,TOOLS neutral;
```

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from typing import Any


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Сохраняйте только последние несколько сообщений, чтобы они помещались в контекстном окне."""
    messages = state["messages"]

    if len(messages) <= 3:
        return None # Никаких изменений не требуется
    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }


agent = create_agent(
    "gpt-5-nano",
    tools=[],
    middleware=[trim_messages],
    checkpointer=InMemorySaver()
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": "привет, меня зовут Боб"}, config)
agent.invoke({"messages": "напиши короткое стихотворение о кошках"}, config)
agent.invoke({"messages": "а теперь то же самое, но о собаках"}, config)
final_response = agent.invoke({"messages": "как меня зовут?"}, config)

final_response["messages"][-1].pretty_print()
"""
================================== Сообщение от ИИ ==================================

Вас зовут Боб. Вы уже говорили мне об этом.
Если вы хотите, чтобы я называл вас по прозвищу или как-то иначе, просто скажите.
"""
```

### После модели

Доступ к кратковременной памяти (состоянию) в промежуточном программном обеспечении [`@after_model`](https://reference.langchain.com/python/langchain/agents/middleware/types/after_model) для обработки сообщений после вызовов модели.

```mermaid theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
%%{
    init: {
        "fontFamily": "monospace",
        "flowchart": {
        "curve": "basis"
        }
    }
}%%
graph TD
    S(["\_\_start\_\_"])
    MODEL(model)
    POST(after_model)
    TOOLS(tools)
    END(["\_\_end\_\_"])
    S --> MODEL
    MODEL --> POST
    POST -.-> END
    POST -.-> TOOLS
    TOOLS --> MODEL
    classDef blueHighlight fill:#DBEAFE,stroke:#2563EB,color:#1E3A8A;
    classDef greenHighlight fill:#DCFCE7,stroke:#16A34A,color:#14532D;
    classDef neutral fill:#F3F4F6,stroke:#9CA3AF,stroke-width:2px,color:#374151;
    class S blueHighlight;
    class END blueHighlight;
    class POST greenHighlight;
    class MODEL,TOOLS neutral;
```

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime


@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Удалить сообщения, содержащие конфиденциальную информацию."""
    STOP_WORDS = ["пароль", "секрет"]
    last_message = state["messages"][-1]
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[validate_response],
    checkpointer=InMemorySaver(),
)
```
