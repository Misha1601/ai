# Потоковая передача

> Потоковая передача обновлений в реальном времени от агентов

LangChain реализует систему потоковой передачи обновлений в реальном времени.

Потоковая передача крайне важна для повышения скорости отклика приложений, созданных на основе больших языковых моделей. Благодаря постепенному отображению выходных данных, даже до того, как будет готов полный ответ, потоковая передача значительно улучшает пользовательский опыт (UX), особенно при работе с задержками в LLM.

## Обзор

Система потоковой передачи LangChain позволяет передавать в ваше приложение обратную связь в реальном времени от запусков агентов.

Что возможно с потоковой передачей LangChain:

* <Icon icon="brain" size={16} /> [**Отслеживайте прогресс агента**](#agent-progress) — получайте обновления состояния после каждого шага агента.
* <Icon icon="binary" size={16} /> [**Отслеживайте токены языковой модели**](#llm-tokens) — отслеживайте токены языковой модели по мере их генерации.
* <Иконка icon="лампочка" size={16} /> [**Токены потокового мышления / рассуждений**](#streaming-thinking-/-reasoning-tokens) — рассуждения поверхностной модели в процессе генерации.
* <Icon icon="table" size={16} /> [**Пользовательские обновления потока**](#custom-updates) — отправка пользовательских сигналов (например, `"Получено 10/100 записей"`).
* <Иконка icon="stack-push" size={16} /> [**Потоковая передача в нескольких режимах**](#stream-multiple-modes) — выберите `обновления` (прогресс агента), `сообщения` (токены LLM + метаданные) или `пользовательские` (произвольные пользовательские данные).

Дополнительные примеры сквозной обработки см. в разделе [распространенные шаблоны](#common-patterns) ниже.

## Поддерживаемые режимы потоковой передачи

Передайте один или несколько следующих потоковых режимов в виде списка в методы [`stream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream) или [`astream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.astream):

| Режим | Описание |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `updates` | Потоковая передача обновлений состояния после каждого шага агента. Если на одном шаге выполняется несколько обновлений (например, запускаются несколько узлов), они передаются по отдельности. |
| `messages` | Потоковая передача кортежей `(токен, метаданные)` от любых узлов графа, в которых вызывается языковая модель. |
| `custom` | Потоковая передача пользовательских данных из узлов вашего графа с помощью потокового модуля записи. |

## Ход выполнения агента

Чтобы отслеживать прогресс агента, используйте методы [`stream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream) или [`astream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.astream) с параметром `stream_mode="updates"`. Это позволяет генерировать событие после каждого шага агента.

Например, если у вас есть агент, который один раз вызывает инструмент, вы должны увидеть следующие обновления:

* **Узел LLM**: [`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage) с запросами на вызов инструмента
* **Узел инструмента**: [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) с результатом выполнения
* **Узел LLM**: окончательный ответ ИИ

```python title="Streaming agent progress" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Получить погоду для указанного города."""

    return f"В {city} всегда солнечно!"
agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
)
for chunk in agent.stream( # [!code highlight]
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode="updates",
    version="v2", # [!code highlight]
):
    if chunk["type"] == "updates": # [!code highlight]
        for step, data in chunk["data"].items(): # [!code highlight]
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")
```

```shell title="Output" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
step: model
content: [{'type': 'tool_call', 'name': 'get_weather', 'args': {'city': 'Сан-Франциско'}, 'id': 'call_OW2NYNsNSKhRZpjW0wm2Aszd'}]

step: tools
content: [{'type': 'text', 'text': "В Сан-Франциско всегда солнечно!"}]

step: model
content: [{'type': 'text', 'text': 'В Сан-Франциско всегда солнечно!'}]
```

## Токены LLM

Чтобы получать токены по мере их генерации языковой моделью, используйте параметр `stream_mode="messages"`. Ниже вы можете увидеть результаты работы инструмента потоковой передачи данных и итоговый ответ.

```python title="Потоковая передача токенов больших языковых моделей" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent


def get_weather(city: str) -> str:
    """Получить погоду для указанного города."""

    return f"В {city} всегда солнечно!"
agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
)
for chunk in agent.stream( # [!code highlight]
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode="messages",
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        print(f"node: {metadata['langgraph_node']}")
        print(f"content: {token.content_blocks}")
        print("\n")
```


## Пользовательские обновления

Чтобы получать обновления от инструментов по мере их выполнения, можно использовать [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/get_stream_writer).

```python title="Потоковая передача пользовательских обновлений" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from langgraph.config import get_stream_writer # [!code highlight]


def get_weather(city: str) -> str:
    """Узнать погоду в указанном городе."""
    writer = get_stream_writer() # [!code highlight]
    # потоковая передача любых произвольных данных
    writer(f"Поиск данных для города: {city}")
    writer(f"Получены данные для города: {city}")
    return f"В {city} всегда солнечно!"

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather],
)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode="custom", # [!code highlight]
    version="v2", # [!code highlight]
):
    if chunk["type"] == "custom": # [!code highlight]
        print(chunk["data"]) # [!code highlight]
```

```shell title="Вывод" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
Поиск данных по городу: Сан-Франциско
Полученные данные по городу: Сан-Франциско
```

<Note>

 Если вы добавите [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/get_stream_writer) внутри вашего инструмента, вы не сможете вызывать инструмент вне контекста выполнения LangGraph.
</Note>

## Потоковая передача в нескольких режимах

Вы можете указать несколько режимов потоковой передачи, передав stream mode в виде списка: `stream_mode=["updates", "custom"]`.

Каждый фрагмент потока представляет собой словарь StreamPart с ключами type, ns и data.  Используйте chunk["type"], чтобы определить режим потока, и chunk["data"], чтобы получить доступ к полезной нагрузке.

```python title="Потоковая передача в нескольких режимах" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from langgraph.config import get_stream_writer


def get_weather(city: str) -> str:
    """Узнать погоду в указанном городе."""
    writer = get_stream_writer()
    writer(f"Поиск данных для города: {city}")
    writer(f"Получены данные для города: {city}")
    return f"В {city} всегда солнечно!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
)

f   or chunk in agent.stream( # [!code highlight]
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode=["updates", "custom"],
    version="v2", # [!code highlight]
):
    print(f"stream_mode: {chunk['type']}") # [!code highlight]
    print(f"content: {chunk['data']}") # [!code highlight]
    print("\n")
```


## Общие шаблоны

Ниже приведены примеры, показывающие распространенные варианты использования потоковой передачи.

### Потоковая передача токенов, связанных с мышлением и рассуждениями
Некоторые модели выполняют внутренние рассуждения, прежде чем выдать окончательный ответ. Вы можете отслеживать эти токены, связанные с мышлением и рассуждениями, по мере их генерации, отфильтровывая [стандартные блоки контента](/oss/python/langchain/messages#standard-content-blocks) по типу `"reasoning"`.

<Note>

 В модели должна быть включена функция вывода рассуждений.

 Смотрите раздел [обоснование] (/oss/python/langchain/models # обоснование) и страницу интеграции вашего провайдера (/oss / python /integrations / providers / обзор) для получения подробной информации о конфигурации.

 Чтобы быстро проверить обоснованность модели, см. [models.dev](https://models.dev).
</Note>

Для потоковой передачи токенов мышления от агента используйте `stream_mode ="messages"` и фильтруйте блоки содержимого рассуждений:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.agents import create_agent
from langchain.messages import AIMessageChunk
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import Runnable


def get_weather(city: str) -> str:
    """Узнай погоду для данного города"."""
    return :"В {городе} всегда солнечно!"


model = ChatAnthropic(
    model_name="claude-sonnet-4-6",
    timeout=None,
    stop=None,
    thinking={"type": "enabled", "budget_tokens": 5000},
)
agent: Runnable = create_agent(
    model=model,
    tools=[get_weather],
)

for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode="messages", # [!code highlight]
):
    if not isinstance(token, AIMessageChunk):
        continue
    reasoning = [b for b in token.content_blocks if b["type"] == "reasoning"]
    text = [b for b in token.content_blocks if b["type"] == "text"]
    if reasoning:
        print(f"[размышления] {reasoning[0]['размышления']}", end="")
    if text:
        print(text[0]["текст"], end="")
```

```shell title="Вывод" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
[thinking] Пользователь спрашивает о погоде в Сан-Франциско. У меня есть инструмент
[thinking] для получения этой информации. Давайте я вызову инструмент get_weather
[thinking] с использованием «Сан-Франциско» в качестве параметра города.
 Погода в Сан-Франциско: в Сан-Франциско всегда солнечно!
```

Это работает одинаково независимо от поставщика модели: LangChain преобразует специфичные для поставщика форматы (блоки `thinking` от Anthropic, сводки `reasoning` от OpenAI и т. д.) в стандартный тип блока контента `"reasoning"` с помощью свойства [`content_blocks`](/oss/python/langchain/messages#standard-content-blocks).

 Чтобы получать токены рассуждений напрямую от чат-модели (без агента), см. [раздел о потоковой передаче с помощью чат-моделей](/oss/python/langchain/models#reasoning).

### Потоковые вызовы инструментов

Возможно, вам захочется транслировать оба варианта:

1. Генерируется частичный JSON в виде [вызовов инструментов] (/oss / python /langchain/models#вызов инструмента)
2. Завершенные, проанализированные вызовы инструмента, которые выполняются

Указание [`stream_mode="messages"`](#llm-токены) приведет к потоковой передаче инкрементных [блоков сообщений] (/oss/python/langchain/messages#streaming-and-chunks), генерируемых всеми вызовами LLM в агенте. Чтобы получить доступ к обработанным сообщениям с помощью проанализированных вызовов инструментов:

1. Если эти сообщения отслеживаются в [состоянии](/oss/python/langchain/agents#memory) (как в узле модели [`create_agent`](/oss/python/langchain/agents)), используйте `stream_mode=["messages", "updates"]` для доступа к обработанным сообщениям через [обновления состояния](#agent-progress) (см. пример ниже).
2. Если эти сообщения не отслеживаются в состоянии, используйте [пользовательские обновления](#custom-updates) или объединяйте фрагменты в цикле потоковой передачи ([следующий раздел](#accessing-completed-messages)).

<Note>

 Если ваш агент включает в себя несколько больших языковых моделей, обратитесь к разделу ниже о [потоковой передаче от субагентов](#streaming-from-sub-agents).
</Note>

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any

from langchain.agents import create_agent
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage


def get_weather(city: str) -> str:
    """Узнайте погоду в указанном городе."""

    return f"В {city} всегда солнечно!"


agent = create_agent("openai:gpt-5.2", tools=[get_weather])


def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)
 # Примечание. весь контент доступен через token.content_blocks


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")


input_message = {"role": "user", "content": "Какая погода в Бостоне?"}
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates"],  # [!code highlight]
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)  # [!code highlight]
    elif chunk["type"] == "updates":  # [!code highlight]
        for source, update in chunk["data"].items():  # [!code highlight]
            if source in ("model", "tools"):  # `source` captures node name
                _render_completed_message(update["messages"][-1])  # [!code highlight]
```

```shell title="Вывод" расширяемая тема={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
[{'name': 'get_weather', 'args': '', 'id': 'call_D3Orjr89KgsLTZ9hTzYv7Hpf', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'city', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '":"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'Boston', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'get_weather', 'args': {'city': 'Бостон'}, 'id': 'call_D3Orjr89KgsLTZ9hTzYv7Hpf', 'type': 'tool_call'}]
Ответ инструмента: [{'type': 'text', 'text': "В Бостоне всегда солнечно!"}]
| Погода| в| Бостоне| такая| **|солнечная|Нью-Йорк|**|.|
```

#### Доступ к завершенным сообщениям

<Note>

 Если завершенные сообщения отслеживаются в [состоянии] агента (/oss / python /langchain/agents#memory), вы можете использовать `stream_mode = ["сообщения", "обновления"]`, как показано в разделе [Вызовы инструментов потоковой передачи] (#streaming-tool-calls) для доступа к завершенным сообщениям во время потоковой передачи.
</Note>

В некоторых случаях завершенные сообщения не отображаются в [обновлениях состояния](#agent-progress). Если у вас есть доступ к внутренним компонентам агента, вы можете использовать [пользовательские обновления](#custom-updates), чтобы получать доступ к этим сообщениям во время потоковой передачи. В противном случае вы можете объединять фрагменты сообщений в цикле потоковой передачи (см. ниже).

 Рассмотрим приведенный ниже пример, в котором мы встраиваем [средство записи потока](#custom-updates) в упрощенное [промежуточное ПО для защиты](/oss/python/langchain/guardrails#after-agent-guardrails). Это промежуточное ПО демонстрирует вызов инструмента для создания структурированной оценки «безопасных/небезопасных» данных (для этого также можно использовать [структурированные выходные данные](/oss/python/langchain/models#structured-output)):

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any, Literal

from langchain.agents.middleware import after_agent, AgentState
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model
from langgraph.config import get_stream_writer # [!code highlight]
from pydantic import BaseModel

class ResponseSafety(BaseModel):
    """Оценивает ответ как безопасный или небезопасный."""
    evaluation: Literal["safe", "unsafe"]


safety_model = init_chat_model("openai:gpt-5.2")

@after_agent(can_jump_to=["end"])
def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Защита на основе модели: используйте большую языковую модель для оценки безопасности ответа."""
    stream_writer = get_stream_writer() # [!code highlight]
    # Получаем ответ модели
    if not state["messages"]:
        return None

    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return None

    # Используйте другую модель для оценки безопасности
    model_with_tools = safety_model.bind_tools([ResponseSafety], tool_choice="any")
    result = model_with_tools.invoke(
        [
            {
                "role": "system",
                "content": "Оцените этот ответ ИИ как в целом безопасный или небезопасный."
            },
            {
                "role": "user",
                "content": f"Ответ ИИ: {last_message.text}"
            }
        ]
    )
    stream_writer(result) # [!code highlight]

    tool_call = result.tool_calls[0]
    if tool_call["args"]["evaluation"] == "unsafe":
        last_message.content = "Я не могу дать такой ответ. Пожалуйста, сформулируйте запрос иначе".
    return None
 ```

 Затем мы можем включить это промежуточное ПО в наш агент и добавить пользовательские потоковые события:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any

from langchain.agents import create_agent
from langchain.messages import AIMessageChunk, AIMessage, AnyMessage


def get_weather(city: str) -> str:
    """Узнайте погоду в указанном городе."""

    return f"В {city} всегда солнечно!"


agent = create_agent(
    model="openai:gpt-5.2",
    tools=[get_weather],
    middleware=[safety_guardrail], # [!code highlight]
)

def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")


input_message = {"role": "user", "content": "Какая погода в Бостоне?"}
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates", "custom"], # [!code highlight]
    version="v2", # [!code highlight]
):
    if chunk["type"] == "messages": # [!code highlight]
        token, metadata = chunk["data"] # [!code highlight]
    if isinstance(token, AIMessageChunk):
        _render_message_chunk(token)
    elif chunk["type"] == "updates": # [!code highlight]
        for source, update in chunk["data"].items(): # [!code highlight]
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
    elif chunk["type"] == "custom": # [!code highlight]
        # доступ к завершенному сообщению в потоке
        print(f"Вызовы инструмента: {chunk['data'].tool_calls}") # [!code highlight]
```

```shell title="Вывод" расширяемая тема={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
[{'name': 'get_weather', 'args': '', 'id': 'call_je6LWgxYzuZ84mmoDalTYMJC', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'city', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '":"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'Boston', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'get_weather', 'args': {'city': 'Бостон'}, 'id': 'call_je6LWgxYzuZ84mmoDalTYMJC', 'type': 'tool_call'}]
Ответ инструмента: [{'type': 'text', 'text': "В Бостоне всегда солнечно!"}]
Погода| в| **|Бостоне|**| **|солнечная|**|.|[{'name': 'ResponseSafety', 'args': '', 'id': 'call_O8VJIbOG4Q9nQF0T8ltVi58O', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'evaluation', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '":"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'safe', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'ResponseSafety', 'args': {'evaluation': 'safe'}, 'id': 'call_O8VJIbOG4Q9nQF0T8ltVi58O', 'type': 'tool_call'}]
```

В качестве альтернативы, если у вас нет возможности добавлять пользовательские события в поток, вы можете объединять фрагменты сообщений в цикле потоковой передачи:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
input_message = {"role": "user", "content": "Какая погода в Бостоне?"}
full_message = None # [!code highlight]
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates"],
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
            full_message = token if full_message is None else full_message + token  # [!code highlight]
            if token.chunk_position == "last":  # [!code highlight]
                if full_message.tool_calls:  # [!code highlight]
                    print(f"Вызовы инструментов: {full_message.tool_calls}") # [!code highlight]
                full_message = None  # [!code highlight]
    elif chunk["type"] == "updates":  # [!code highlight]
        for source, update in chunk["data"].items():  # [!code highlight]
            if source == "tools":
                _render_completed_message(update["messages"][-1])
```

### Потоковая передача с human-in-the-loop

Чтобы обрабатывать человеко-в-цикле [прерывания] (/oss /python /langchain /человеко-в-цикле), мы основываемся на [приведенном выше примере] (#вызовы потокового инструмента):

1. Мы настраиваем агент с помощью [промежуточного программного обеспечения human-in-the-loop и контрольной точки] (/oss/python/langchain/human-in-the-loop#конфигурирование прерываний)
2. Мы собираем прерывания, возникающие в режиме потока `"обновления"`
3. Мы реагируем на эти прерывания с помощью [команды](/oss/python/langchain/human-in-the-loop#responding-to-interrupts)

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, Interrupt


def get_weather(city: str) -> str:
    """Узнать погоду в указанном городе."""

    return f"В {city} всегда солнечно!"


checkpointer = InMemorySaver()

agent = create_agent(
    "openai:gpt-5.2",
    tools=[get_weather],
    middleware=[  # [!code highlight]
        HumanInTheLoopMiddleware(interrupt_on={"get_weather": True}),  # [!code highlight]
    ],  # [!code highlight]
    checkpointer=checkpointer,  # [!code highlight]
)


def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Вызовы инструмента: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Ответ инструмента: {message.content_blocks}")


def _render_interrupt(interrupt: Interrupt) -> None:  # [!code highlight]
    interrupts = interrupt.value  # [!code highlight]
    for request in interrupts["action_requests"]:  # [!code highlight]
        print(request["description"])  # [!code highlight]


input_message = {
    "role": "user",
    "content": (
        "Можете посмотреть погоду в Бостоне и Сан-Франциско?"
    ),
}
config = {"configurable": {"thread_id": "some_id"}}  # [!code highlight]
interrupts = []  # [!code highlight]
for chunk in agent.stream(
    {"messages": [input_message]},
    config=config,  # [!code highlight]
    stream_mode=["messages", "updates"],
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":  # [!code highlight]
        for source, update in chunk["data"].items():  # [!code highlight]
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
            if source == "__interrupt__":  # [!code highlight]
                interrupts.extend(update)  # [!code highlight]
                _render_interrupt(update[0])  # [!code highlight]
```

```shell title="Вывод" расширяемая тема={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
[{'name': 'get_weather', 'args': '', 'id': 'call_GOwNaQHeqMixay2qy80padfE', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"ci', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'ty": ', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"Bosto', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'n"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': 'get_weather', 'args': '', 'id': 'call_Ndb4jvWm2uMA0JDQXu37wDH6', 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"ci', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'ty": ', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"San F', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'ranc', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'isco"', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '}', 'id': None, 'index': 1, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'get_weather', 'args': {'city': 'Boston'}, 'id': 'call_GOwNaQHeqMixay2qy80padfE', 'type': 'tool_call'}, {'name': 'get_weather', 'args': {'city': 'San Francisco'}, 'id': 'call_Ndb4jvWm2uMA0JDQXu37wDH6', 'type': 'tool_call'}]
Для запуска инструмента требуется подтверждение

Инструмент: get_weather
Аргументы: {'город': 'Бостон'}
Для запуска инструмента требуется подтверждение

Инструмент: get_weather
Аргументы: {'город': 'Сан-Франциско'}
```

Далее мы собираем [decision](/oss/python/langchain/human-in-the-loop#interrupt-decision-types) для каждого прерывания. Важно отметить, что порядок принятия решений должен соответствовать порядку действий, которые мы собрали.

Для наглядности мы отредактируем один вызов инструмента и примем другой:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
def _get_interrupt_decisions(interrupt: Interrupt) -> list[dict]:
    return [
        {
            "type": "edit",
            "edited_action": {
                "name": "get_weather",
                "args": {"city": "Boston, U.K."},
            },
        }
        if "boston" in request["description"].lower()
        else {"type": "approve"}
        for request in interrupt.value["action_requests"]
    ]

decisions = {}
for interrupt in interrupts:
    decisions[interrupt.id] = {
        "decisions": _get_interrupt_decisions(interrupt)
    }

decisions
```

```shell title="Output" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
{
    'a96c40474e429d661b5b32a8d86f0f3e': {
        'decisions': [
            {
                'type': 'edit',
                 'edited_action': {
                     'name': 'get_weather',
                     'args': {'city': 'Boston, U.K.'}
                 }
            },
            {'type': 'approve'},
        ]
    }
}
```

Затем мы можем возобновить работу, передав [команду](/oss/python/langchain/human-in-the-loop#responding-to-interrupts) в тот же цикл потоковой передачи:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
interrupts = []
for chunk in agent.stream(
    Command(resume=decisions),  # [!code highlight]
    config=config,
    stream_mode=["messages", "updates"],
    version="v2",  # [!code highlight]
):
    # Streaming loop is unchanged
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":  # [!code highlight]
        for source, update in chunk["data"].items():  # [!code highlight]
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
            if source == "__interrupt__":
                interrupts.extend(update)
                _render_interrupt(update[0])
```

```shell title="Вывод" theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
Ответ инструмента: [{'type': 'text', 'text': "В Бостоне, Великобритания, всегда солнечно!"}]
Ответ инструмента: [{'type': 'text', 'text': "В Сан-Франциско всегда солнечно!"}]
-| **|Бостон|***|: В|Бостоне|| всегда| солнечно|,| U|.K|.|
|-|***|Сан|Франциско|***|: В|Сан|Франциско|| всегда| солнечно|!|
```

### Потоковая передача от субагентов

Когда в любой точке агента имеется несколько LLM, часто необходимо определять неоднозначность источника сообщений по мере их генерации.

Для этого при создании каждого агента передавайте ему [`name`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent\(name\)). Это имя будет доступно в метаданных через ключ `lc_agent_name` при потоковой передаче в режиме `"messages"`.

Ниже мы обновляем пример [streaming tool calls](#streaming-tool-calls):

1. Мы заменяем наш инструмент на инструмент `call_weather_agent`, который внутренне вызывает агента.
2. Мы добавляем `name` к каждому агенту.
3. При создании потока мы указываем [`subgraphs=True`](/oss/python/langgraph/use-subgraphs#stream-subgraph-outputs).
4. Обработка потока идентична предыдущей, но мы добавляем логику для отслеживания того, какой агент активен, с помощью параметра `name` функции `create_agent`.

<Tip>

 Когда вы задаете `имя" агенту, это имя также привязывается к любому "целевому сообщению", сгенерированному этим агентом.
</Tip>

Сначала мы создаем агента:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, AnyMessage


def get_weather(city: str) -> str:
    """Узнайте погоду в указанном городе."""

     return f"В {городе} всегда солнечно!"


weather_model = init_chat_model("openai:gpt-5.2")
weather_agent = create_agent(
    model=weather_model,
    tools=[get_weather],
    name="weather_agent",  # [!code highlight]
)


def call_weather_agent(query: str) -> str:
 """Запросите данные у погодного агента."""
    result = weather_agent.invoke({
    "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].text


supervisor_model = init_chat_model("openai:gpt-5.2")
agent = create_agent(
    model=supervisor_model,
    tools=[call_weather_agent],
    name="supervisor",  # [!code highlight]
)

Далее мы добавляем в цикл потоковой передачи логику, которая сообщает, какой агент генерирует токены:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")


input_message = {"role": "user", "content": "What is the weather in Boston?"}
current_agent = None  # [!code highlight]
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates"],
    subgraphs=True,  # [!code highlight]
    version="v2",  # [!code highlight]
):
    if chunk["type"] == "messages":  # [!code highlight]
        token, metadata = chunk["data"]  # [!code highlight]
        if agent_name := metadata.get("lc_agent_name"):  # [!code highlight]
            if agent_name != current_agent:  # [!code highlight]
                print(f"🤖 {agent_name}: ")  # [!code highlight]
                current_agent = agent_name  # [!code highlight]
        if isinstance(token, AIMessage):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":  # [!code highlight]
        for source, update in chunk["data"].items():  # [!code highlight]
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
```

```shell title="Output" expandable theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
🤖 supervisor:
[{'name': 'call_weather_agent', 'args': '', 'id': 'call_asorzUf0mB6sb7MiKfgojp7I', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'query', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '":"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'Boston', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': ' weather', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': ' right', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': ' now', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': ' and', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': " today's", 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': ' forecast', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'call_weather_agent', 'args': {'query': "Погода в Бостоне сейчас и прогноз на сегодня"}, 'id': 'call_asorzUf0mB6sb7MiKfgojp7I', 'type': 'tool_call'}]
🤖 weather_agent:
[{'name': 'get_weather', 'args': '', 'id': 'call_LZ89lT8fW6w8vqck5pZeaDIx', 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '{"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'city', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '":"', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': 'Boston', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
[{'name': None, 'args': '"}', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
Вызовы инструмента: [{'name': 'get_weather', 'args': {'city': 'Бостон'}, 'id': 'call_LZ89lT8fW6w8vqck5pZeaDIx', 'type': 'tool_call'}]
Ответ инструмента: [{'type': 'text', 'text': "В Бостоне всегда солнечно!"}]
Погода в Бостоне| сейчас|:| **|Солнечно|**|.

|Прогноз на сегодня| в Бостоне|:| **|Солнечно| весь| день|**|.|Ответ инструмента: [{'type': 'text', 'text': 'Погода в Бостоне сейчас: **солнечно**.\n\nПрогноз погоды в Бостоне на сегодня: **солнечно весь день**.'}]
🤖 супервайзер:
Бостон| погода | прямо| сейчас|: | **| Солнечно |**|.

|Сегодня| прогноз| для| Бостона|: | **| Солнечно | весь| день|**|.|
```

## Отключить потоковую передачу

В некоторых приложениях может потребоваться отключить потоковую передачу отдельных токенов для данной модели. Это полезно, когда:

* Работа с [мультиагентными] системами (/ oss / python / langchain / multi-agent) для управления тем, какие агенты передают свои выходные данные
* Смешивание моделей, поддерживающих потоковую передачу, с моделями, которые ее не поддерживают
* Развертывание в [LangSmith](/langsmith/home) с целью предотвращения потоковой передачи определенных выходных данных модели на клиентское устройство

При инициализации модели установите `streaming=False`.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4.1",
    streaming=False  # [!code highlight]
)
```

<Tip>

 При развертывании в LangSmith установите `streaming = False` для любых моделей, выходные данные которых вы не хотите передавать клиенту в потоковом режиме. Это настраивается в вашем коде graph перед развертыванием.
</Tip>

<Note>

 Не все интеграции с моделями чатов поддерживают параметр `streaming`. Если ваша модель его не поддерживает, используйте вместо этого `disable_streaming= True`. Этот параметр доступен во всех моделях чатов через базовый класс.
</Note>

Смотрите [Руководство по потоковой передаче LangGraph] (/oss / python /langgraph/streaming#отключить потоковую передачу для конкретных моделей чатов) для получения более подробной информации.

# формат потоковой передачи # v2

<Note>

 Требуется LangGraph >= 1.1.
</Note>

Передайте `version ="v2"` в `stream()` или `astream ()`, чтобы получить унифицированный формат вывода. Каждый фрагмент представляет собой дикт "StreamPart" с ключами "type", "ns" и "data" — одинаковой формы независимо от режима потока или количества режимов:

<CodeGroup>

 ```python v2 (новый) theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
 # Унифицированный формат — больше никакой распаковки кортежей
 for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Какая погода в Сан-Франциско?"}]},
    stream_mode=["updates", "custom"],
    version="v2",
 ):
    print(chunk["type"]) # "updates" или "custom"
    print(chunk["data"]) # полезная нагрузка
 ```

 ```python v1 (текущий вариант по умолчанию) theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
 # Необходимо распаковать кортежи (mode, data)
 for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["updates", "custom"],
 ):
    print(mode)   # "updates" or "custom"
    print(chunk)  # payload
 ```
</CodeGroup>

The v2 format also improves `invoke()` — it returns a `GraphOutput` object with `.value` and `.interrupts` attributes, cleanly separating state from interrupt metadata:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    version="v2",
)
print(result.value)       # state (dict, Pydantic model, or dataclass)
print(result.interrupts)  # tuple of Interrupt objects (empty if none)
```

See the [LangGraph streaming docs](/oss/python/langgraph/streaming#stream-output-format-v2) for more details on the v2 format, including type narrowing, Pydantic/dataclass coercion, and subgraph streaming.

## Related

* [Frontend streaming](/oss/python/langchain/streaming/frontend)—Build React UIs with `useStream` for real-time agent interactions
* [Streaming with chat models](/oss/python/langchain/models#stream)—Stream tokens directly from a chat model without using an agent or graph
* [Reasoning with chat models](/oss/python/langchain/models#reasoning)—Configure and access reasoning output from chat models
* [Standard content blocks](/oss/python/langchain/messages#standard-content-blocks)—Understand the normalized content block format used for reasoning, text, and other content types
* [Streaming with human-in-the-loop](/oss/python/langchain/human-in-the-loop#streaming-with-human-in-the-loop)—Stream agent progress while handling interrupts for human review
* [LangGraph streaming](/oss/python/langgraph/streaming)—Advanced streaming options including `values`, `debug` modes, and subgraph streaming
