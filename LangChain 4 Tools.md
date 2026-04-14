# Инструменты

Инструменты расширяют возможности [агентов] (/oss / python / langchain / agents) - позволяя им извлекать данные в реальном времени, выполнять код, запрашивать внешние базы данных и предпринимать действия в мире.

По сути, инструменты - это вызываемые функции с четко определенными входами и выходами, которые передаются в [модель чата] (/oss / python /langchain /models). Модель решает, когда вызывать инструмент, на основе контекста диалога и какие входные аргументы предоставлять.

<Tip>
Подробнее о том, как модели обрабатывают вызовы инструментов, см. в разделе [Вызов инструмента] (/oss/python/langchain/models#вызов инструмента).
</Tip>

## Создание инструментов

### Определение базового инструмента

Самый простой способ создать инструмент — использовать декоратор [`@tool`](https://reference.langchain.com/python/langchain-core/tools/convert/tool). По умолчанию строка документации функции становится описанием инструмента, которое помогает модели понять, когда его следует использовать:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Выполните поиск в базе данных клиентов по записям, соответствующим запросу.

    Args:
        query: искомые поисковые запросы
        limit: максимальное количество возвращаемых результатов
    """
    return f"Найдено {limit} результатов по запросу '{query}'"
```

Подсказки типов **обязательны**, так как они определяют схему входных данных инструмента. Строка документации должна быть информативной и краткой, чтобы помочь модели понять назначение инструмента.

<Note>
**Использование инструментов на стороне сервера:** некоторые чат-модели оснащены встроенными инструментами (веб-поиском, интерпретаторами кода), которые выполняются на стороне сервера. Подробнее см. в разделе [Использование инструментов на стороне сервера](#server-side-tool-use).
</Note>

<Warning>
Для названий инструментов лучше использовать формат `snake_case` (например, `web_search` вместо `Web Search`). У некоторых поставщиков моделей возникают проблемы с именами, содержащими пробелы или специальные символы, или они отклоняют такие имена. Использование буквенно-цифровых символов, подчеркиваний и дефисов помогает повысить совместимость с другими поставщиками.
</Warning>

### Настройка свойств инструмента

#### Пользовательское название инструмента

По умолчанию название инструмента совпадает с названием функции. Используйте его, когда вам нужно что-то более информативное:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
@tool("web_search") # Пользовательское название
def search(query: str) -> str:
    """Найдите информацию в интернете."""
    return f"Результаты поиска по запросу: {запрос}"
print(search.name) # web_search
```

#### Пользовательское описание инструмента

Измените автоматически сгенерированное описание инструмента, чтобы сделать рекомендации по использованию модели более понятными:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
@tool("calculator", description="Выполняет арифметические вычисления. Используйте это для любых математических задач.")
def calc(выражение: str) -> str:
    """Вычисляйте математические выражения."""
    return str(eval(выражение))
```

### Расширенное определение схемы

Определение сложных входных данных с помощью моделей Pydantic или схем JSON:

<CodeGroup>
 ```python Модель Pydantic theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
 from pydantic import BaseModel, Field
 from typing import Literal

 class WeatherInput(BaseModel):
    """Ввод данных для запросов о погоде."""
    location: str = Field(description="Название города или координаты")
    units: Literal["градусы Цельсия", "градусы Фаренгейта"] = Field(
        default="градусы Цельсия",
        description="Предпочтительная единица измерения температуры"
    )
    include_forecast: bool = Field(
        default=False,
        description="Включить прогноз на 5 дней"
    )

 @tool(args_schema=WeatherInput)
 def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Узнайте текущую погоду и прогноз на выбор."""
    temp = 22, if units == "celsius", иначе 72
    result = f"Текущая погода в {location}: {temp} градусов {units[0].upper()}"
    if include_forecast:
        result += "\nСледующие 5 дней: солнечно"
    return result
 ```

 ```python Схема JSON theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
 weather_schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "units": {"type": "string"},
        "include_forecast": {"type": "boolean"}
    },
    "required": ["location", "units", "include_forecast"]
 }

 @tool(args_schema=weather_schema)
 def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Получить текущую погоду и, при необходимости, прогноз."""
    temp = 22, if units == "celsius", else 72
    result = f"Текущая погода в {location}: {temp} градусов {units[0].upper()}"
    if include_forecast:
        result += "\nСледующие 5 дней: солнечно"
    return result
 ```

</CodeGroup>

### Зарезервированные имена аргументов

Следующие имена параметров являются зарезервированными и не могут использоваться в качестве аргументов инструмента. Использование этих имен приведет к ошибкам во время выполнения.

| Имя параметра | Назначение |
| -------------- | ---------------------------------------------------------------------- |
| `config` | Зарезервировано для внутренней передачи `RunnableConfig` инструментам |
| `runtime` | Зарезервировано для параметра `ToolRuntime` (доступ к состоянию, контексту, хранилищу) |

Для доступа к информации о среде выполнения используйте [`ToolRuntime`](https://reference.langchain.com/python/langchain/tools/#langchain.tools.ToolRuntime) параметр вместо того, чтобы называть свои собственные аргументы `config` или `runtime`.

## Контекст доступа

Инструменты наиболее эффективны, когда они могут получать доступ к информации о времени выполнения, такой как история разговоров, пользовательские данные и постоянная память. В этом разделе описывается, как получить доступ к этой информации и обновить ее из ваших инструментов.

Инструменты могут получать доступ к информации о среде выполнения через параметр [`ToolRuntime`](https://reference.langchain.com/python/langchain/tools/#langchain.tools.ToolRuntime), который предоставляет:

| Компонент | Описание | Пример использования |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Состояние** | Кратковременная память — изменяемые данные, существующие для текущего диалога (сообщения, счетчики, пользовательские поля) | Доступ к истории переписки, отслеживание количества вызовов инструмента |
| **Контекст** | Неизменяемая конфигурация, передаваемая при вызове (идентификаторы пользователей, информация о сеансе) | Персонализация ответов в зависимости от личности пользователя |
| **Хранилище** | Долговременная память — постоянные данные, сохраняющиеся между сеансами общения | Сохраняйте пользовательские настройки, поддерживайте базу знаний |
| **Потоковое записывающее устройство** | Выдача обновлений в режиме реального времени во время работы инструмента | Отображение хода выполнения длительных операций |
| **Информация о выполнении** | Идентификатор и информация о повторных попытках для текущего выполнения (идентификатор потока, идентификатор запуска, номер попытки) | Доступ к идентификаторам потоков/запусков, настройка поведения в зависимости от состояния повторных попыток |
| **Информация о сервере** | Метаданные сервера при работе на LangGraph Server (идентификатор помощника, идентификатор графа, информация об аутентифицированном пользователе) | Идентификатор помощника, идентификатор графа или информация об аутентифицированном пользователе |
| **Конфигурация** | [`RunnableConfig`](https://reference.langchain.com/python/langchain-core/runnables/config/RunnableConfig) для выполнения | Доступ к обратным вызовам, тегам и метаданным |
| **Идентификатор вызова инструмента** | Уникальный идентификатор текущего вызова инструмента | Сопоставление вызовов инструментов с журналами и вызовами моделей |

```mermaid  theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
graph LR
    %% Runtime Context
    subgraph "🔧 Tool Runtime Context"
        A[Tool Call] --> B[ToolRuntime]
        B --> C[State Access]
        B --> D[Context Access]
        B --> E[Store Access]
        B --> F[Stream Writer]
    end

    %% Available Resources
    subgraph "📊 Available Resources"
        C --> G[Messages]
        C --> H[Custom State]
        D --> I[User ID]
        D --> J[Session Info]
        E --> K[Long-term Memory]
        E --> L[User Preferences]
    end

    %% Tool Capabilities
    subgraph "⚡ Enhanced Tool Capabilities"
        M[Context-Aware Tools]
        N[Stateful Tools]
        O[Memory-Enabled Tools]
        P[Streaming Tools]
    end

    %% Connections
    G --> M
    H --> N
    I --> M
    J --> M
    K --> O
    L --> O
    F --> P

    classDef trigger fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    classDef process fill:#DBEAFE,stroke:#2563EB,stroke-width:2px,color:#1E3A8A
    classDef output fill:#F3E8FF,stroke:#9333EA,stroke-width:2px,color:#581C87
    classDef neutral fill:#F3F4F6,stroke:#9CA3AF,stroke-width:2px,color:#374151

    class A trigger
    class B,C,D,E,F process
    class G,H,I,J,K,L neutral
    class M,N,O,P output
```

### Кратковременная память (состояние)

Состояние — это кратковременная память, существующая на протяжении всего диалога. Она включает в себя историю сообщений и все пользовательские поля, которые вы определяете в [состоянии графа](/oss/python/langgraph/graph-api#state).

<Info>
  Добавьте `runtime: ToolRuntime` в сигнатуру вашего инструмента, чтобы получить доступ к состоянию. Этот параметр автоматически добавляется и скрыт от большой языковой модели — он не отображается в схеме инструмента.
</Info>

#### Доступ к состоянию

Инструменты могут получать доступ к текущему состоянию диалога с помощью `runtime.state`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage

@tool
def get_last_user_message(runtime: ToolRuntime) -> str:
    """Получить последнее сообщение от пользователя."""
    messages = runtime.state["messages"]

    # Найдите последнее сообщение от человека
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
        return message.content
    return "Пользовательских сообщений не найдено"

# Доступ к пользовательским полям состояния
@tool
def get_user_preference(
     pref_name: str,
     runtime: ToolRuntime
) -> str:
     """Получить значение пользовательского предпочтения."""
     preferences = runtime.state.get("user_preferences", {})
     return preferences.get(pref_name, "Не задано")
```

<Warning>
 Параметр `runtime` скрыт от модели. В приведенном выше примере модель видит только `pref_name` в схеме инструмента.
</Warning>

#### Состояние обновления

Используйте [`Command`](https://reference.langchain.com/python/langgraph/types/Command) для обновления состояния агента. Это полезно для инструментов, которым необходимо обновлять пользовательские поля состояния:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langgraph.types import Command
from langchain.tools import tool

@tool
def set_user_name(new_name: str) -> Command:
    """Установите имя пользователя в состоянии беседы."""
    return Command(update={"user_name": new_name})
```

<Tip>
    Если инструменты обновляют переменные состояния, рассмотрите возможность определения [reducer](/oss/python/langgraph/graph-api#reducers) для этих полей. Поскольку большие языковые модели могут параллельно вызывать несколько инструментов, редьюсер определяет, как разрешать конфликты, возникающие при одновременном обновлении одного и того же поля состояния несколькими инструментами.
</Tip>

### Контекст

Контекст предоставляет неизменяемые данные конфигурации, которые передаются при вызове. Используйте его для идентификаторов пользователей, данных сеанса или настроек приложения, которые не должны меняться во время разговора.

 Доступ к контексту осуществляется через `runtime.context`:

```python  theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime


USER_DATABASE = {
    "user123": {
        "name": "Alice Johnson",
        "account_type": "Premium",
        "balance": 5000,
        "email": "alice@example.com"
    },
    "user456": {
        "name": "Bob Smith",
        "account_type": "Standard",
        "balance": 1200,
        "email": "bob@example.com"
    }
}

@dataclass
class UserContext:
    user_id: str

@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Получить информацию об учетной записи текущего пользователя."""
    user_id = runtime.context.user_id

    if user_id in USER_DATABASE:
        user = USER_DATABASE[user_id]
        return f"Account holder: {user['name']}\nType: {user['account_type']}\nBalance: ${user['balance']}"
    return "User not found"

model = ChatOpenAI(model="gpt-4.1")
agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,
    system_prompt="Вы — финансовый консультант."
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Каков мой текущий баланс?"}]},
    context=UserContext(user_id="user123")
)
```

### Долгосрочная память (хранилище)

[`BaseStore`](https://reference.langchain.com/python/langchain-core/stores/BaseStore) обеспечивает постоянное хранение данных, которые сохраняются между сеансами. В отличие от состояния (кратковременной памяти), данные, сохраненные в хранилище, остаются доступными в последующих сеансах.

Доступ к хранилищу осуществляется через `runtime.store`. Для организации данных в хранилище используется шаблон «namespace/key»:

<Tip>
    Для производственных развертываний используйте реализацию постоянного хранилища, например [`PostgresStore`](https://reference.langchain.com/python/langgraph/store/#langgraph.store.postgres.PostgresStore), вместо `InMemoryStore`. Подробнее о настройке см. в [документации по работе с памятью](/oss/python/langgraph/memory).
</Tip>

```python расширяемая тема={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from typing import Any
from langgraph.store.memory import InMemoryStore
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI

# Доступ к памяти
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Поиск информации о пользователе."""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

# Обновление памяти
@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """Сохранить информацию о пользователе."""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "Информация о пользователе успешно сохранена."

model = ChatOpenAI(model="gpt-4.1")

store = InMemoryStore()
agent = create_agent(
    model,
    tools=[get_user_info, save_user_info],
    store=store
)

# Первый сеанс: сохранение информации о пользователе
agent.invoke({
    "messages": [{"role": "user", "content": "Сохранить следующего пользователя: userid: abc123, имя: Foo, возраст: 25, электронная почта: foo@langchain.dev"}]
})

# Второй сеанс: получение информации о пользователе
agent.invoke({
    "messages": [{"role": "user", "content": "Получить информацию о пользователе с идентификатором 'abc123'"}]
})
# Вот информация о пользователе с идентификатором "abc123":
# - Имя: Foo
# - Возраст: 25
# - Электронная почта: foo@langchain.dev
```

### Stream writer

Транслируйте обновления инструментов в режиме реального времени во время выполнения. Это полезно для предоставления пользователям обратной связи о ходе выполнения во время длительных операций.

Используйте `runtime.stream_writer` для отправки пользовательских обновлений:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime

@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Получить погоду для указанного города."""
    writer = runtime.stream_writer
    # Потоковая передача пользовательских обновлений по мере выполнения инструмента
    writer(f"Поиск данных для города: {city}")
    writer(f"Получены данные для города: {city}")

    return f"В {city} всегда солнечно!"
```

<Note>
    Если вы используете `runtime.stream_writer` в своем инструменте, он должен быть запущен в контексте выполнения LangGraph. Подробнее см. в разделе [Потоковая передача](/oss/python/langchain/streaming).
</Note>

### Информация о выполнении

Получите доступ к идентификатору потока, идентификатору выполнения и состоянию повторных попыток из инструмента с помощью `runtime.execution_info`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime

@tool
def log_execution_context(runtime: ToolRuntime) -> str:
    """Информация об идентификаторе выполнения."""
    info = runtime.execution_info
    print(f"Поток: {info.thread_id}, выполнение: {info.run_id}") # [!code highlight]
    print(f"Попытка: {info.node_attempt}")
    return "завершено"
```

<Note>
    Требуется версия `deepagents>=0.5.0` (или `langgraph>=1.1.5`).
</Note>

### Информация о сервере

Если ваш инструмент работает на сервере LangGraph, вы можете получить доступ к идентификатору помощника, идентификатору графа и имени пользователя, прошедшего аутентификацию, через `runtime.server_info`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime

@tool
def get_assistant_scoped_data(runtime: ToolRuntime) -> str:
     """Получить данные, относящиеся к текущему помощнику."""
     server = runtime.server_info
     if server is not None:
         print(f"Помощник: {server.assistant_id}, Граф: {server.graph_id}") # [!code highlight]
     if server.user is not None:
        print(f"Пользователь: {server.user.identity}") # [!code highlight]
     return "done"
```

Значение `server_info` равно `None`, когда инструмент не запущен на сервере LangGraph (например, во время локальной разработки или тестирования).

<Note>
    Требуется `deepagents>= 0.5.0` (или `langgraph>=1.1.5`).
</Note>

## ToolNode

[`ToolNode`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.tool_node.ToolNode) — это готовый узел, который запускает инструменты в рабочих процессах LangGraph. Он автоматически обеспечивает параллельное выполнение инструментов, обработку ошибок и внедрение состояний.

<Info>
    Для пользовательских рабочих процессов, где вам нужен детальный контроль над шаблонами выполнения инструмента, используйте [`ToolNode`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.tool_node.ToolNode) вместо [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent). Это строительный блок, обеспечивающий выполнение инструмента agent.
</Info>

### Базовое использование

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END

@tool
def search(query: str) -> str:
    """Поиск информации."""
    return f"Результаты по запросу: {query}"

@tool
def calculator(expression: str) -> str:
    """Вычислите математическое выражение."""
    return str(eval(expression))

# Создайте ToolNode с вашими инструментами
tool_node = ToolNode([search, calculator])

# Используйте в графе
builder = StateGraph(MessagesState)
builder.add_node("tools", tool_node)
# ... добавьте другие узлы и связи
```

### Возвращаемые значения инструментов

Вы можете выбрать разные возвращаемые значения для своих инструментов:

* Возвращайте `string` для удобочитаемых результатов.
* Возвращайте `object` для структурированных результатов, которые должна проанализировать модель.
* Возвращайте `Command` с необязательным сообщением, если вам нужно записать данные в состояние.

#### Возвращает строку

Возвращает строку, когда инструмент должен предоставить модели обычный текст для чтения и использования в следующем ответе.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Узнать погоду в городе."""
    return f"Сейчас в {city} солнечно."
```

Поведение:
* Возвращаемое значение преобразуется в `ToolMessage`.
* Модель видит этот текст и решает, что делать дальше.
* Поля состояния агента не изменяются, если модель или другой инструмент не сделают этого позже.

Используйте это, когда результатом является текст, понятный человеку.

#### Вернуть объект

Возвращайте объект (например, `dict`), когда ваш инструмент создает структурированные данные, которые должна проверять модель.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool

@tool
def get_weather_data(city: str) -> dict:
    """Получить структурированные данные о погоде в городе."""
    return {
        "city": city,
        "temperature_c": 22,
        "conditions": "sunny",
    }
```

Поведение:
* Объект сериализуется и отправляется обратно в качестве вывода инструмента.
* Модель может считывать определенные поля и обрабатывать их.
* Как и в случае со строковыми возвратами, это не приводит к непосредственному обновлению состояния графа.

Используйте этот вариант, когда для последующих рассуждений лучше подходят явные поля, а не текст произвольной формы.

#### Вернуть команду

Возвращайте [`Command`](https://reference.langchain.com/python/langgraph/types/Command), когда инструменту нужно обновить состояние графа (например, задать пользовательские настройки или состояние приложения). Вы можете вернуть `Command` с `ToolMessage` или без него. Если модели нужно убедиться, что инструмент сработал успешно (например, чтобы подтвердить изменение настроек), включите в обновление `ToolMessage`, используя `runtime.tool_call_id` в качестве параметра `tool_call_id`.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    """Установите предпочтительный язык ответа."""
    return Command(
        update={
            "preferred_language": language,
            "messages": [
                ToolMessage(
                    content=f"Язык установлен на {language}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
```

Поведение:
* Команда обновляет состояние с помощью `update`.
* Обновленное состояние доступно для последующих шагов в том же запуске.
* Используйте редукторы для полей, которые могут обновляться параллельными вызовами инструмента.

Используйте это, когда инструмент не просто возвращает данные, но и изменяет состояние агента.

### Обработка ошибок

Настройте способ обработки ошибок инструмента. Смотрите ссылку на API [`ToolNode`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.tool_node.ToolNode) для получения всех параметров.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langgraph.prebuilt import ToolNode

# По умолчанию: перехватывать ошибки при вызове, повторно вызывать ошибки при выполнении
tool_node = ToolNode(tools)

# Перехватываем все ошибки и возвращаем сообщение об ошибке в LLM
tool_node = ToolNode(tools, handle_tool_errors=True)

# Пользовательское сообщение об ошибке
tool_node = ToolNode(tools, handle_tool_errors="Что-то пошло не так, попробуйте еще раз.")

# Пользовательский обработчик ошибок
def handle_error(e: ValueError) -> str:
    return f"Неверный ввод: {e}"

tool_node = ToolNode(tools, handle_tool_errors=handle_error)

# Перехватываем только определенные типы исключений
tool_node = ToolNode(tools, handle_tool_errors=(ValueError, TypeError))
```

### Маршрут с условием tools_condition

Используйте [`tools_condition`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.tool_node.tools_condition) для условной маршрутизации в зависимости от того, выполняла ли языковая модель вызовы инструментов:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, START, END

builder = StateGraph(MessagesState)
builder.add_node("llm", call_llm)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition) # Маршруты к "tools" или END
builder.add_edge("tools", "llm")

graph = builder.compile()
```

### Внедрение состояния

Инструменты могут получать доступ к текущему состоянию графа через [`ToolRuntime`](https://reference.langchain.com/python/langchain/tools/#langchain.tools.ToolRuntime):

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.tools import tool, ToolRuntime
from langgraph.prebuilt import ToolNode

@tool
def get_message_count(runtime: ToolRuntime) -> str:
     """Получить количество сообщений в диалоге."""
    messages = runtime.state["messages"]
    return f"Есть сообщения {len(messages)}".

tool_node = ToolNode([get_message_count])
```

Дополнительные сведения о доступе к состоянию, контексту и долговременной памяти из инструментов см. в разделе [Контекст доступа] (#доступ-контекст).

## Готовые инструменты

LangChain предоставляет большую коллекцию готовых инструментов и подборок утилит для выполнения таких распространенных задач, как веб-поиск, интерпретация кода, доступ к базе данных и многое другое. Эти готовые к использованию инструменты могут быть непосредственно интегрированы в ваши агенты без написания пользовательского кода.

Смотрите страницу интеграции [инструменты и подборки инструментов] (/oss/python/интеграции/tools) для получения полного списка доступных инструментов, упорядоченного по категориям.

## Использование инструментов на стороне сервера

Некоторые модели чатов имеют встроенные инструменты, которые выполняются поставщиком моделей на стороне сервера. К ним относятся такие возможности, как веб-поиск и интерпретаторы кода, которые не требуют от вас определения или размещения логики инструмента.

Подробнее о включении и использовании этих встроенных инструментов см. на отдельных [страницах, посвященных интеграции моделей чата](/oss/python/integrations/providers) и в [документации по вызову инструментов](/oss/python/langchain/models#server-side-tool-use).
