
# Структурированный вывод

Структурированный вывод позволяет агентам возвращать данные в определенном, предсказуемом формате. Вместо анализа ответов на естественном языке вы получаете структурированные данные в виде объектов JSON, [моделей Pydantic](https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage) или классов данных, которые ваше приложение может использовать напрямую.

<Tip>

 На этой странице рассказывается о структурированном выводе с помощью агентов, использующих функцию `create_agent`. Чтобы использовать структурированный вывод непосредственно в модели (вне агентов), см. [Модели — структурированный вывод](/oss/python/langchain/models#structured-output).
</Tip>

Функция [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) в LangChain автоматически обрабатывает структурированный вывод. Пользователь задает желаемую схему структурированного вывода, и когда модель генерирует структурированные данные, они фиксируются, проверяются и возвращаются в виде ключа `'structured_response'` в состоянии агента.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
def create_agent(
    ...
    response_format: Union[
        ToolStrategy[StructuredResponseT],
        ProviderStrategy[StructuredResponseT],
        type[StructuredResponseT],
        None,
    ]
)
```

## Формат ответа

Используйте `response_format` для управления тем, как агент возвращает структурированные данные:

* **`ToolStrategy [StructuredResponseT]` **: использует вызов инструмента для структурированного вывода
* **`ProviderStrategy[StructuredResponseT]` **: Использует собственные структурированные выходные данные поставщика.
* **`type[StructuredResponseT]` **: Тип схемы - автоматически выбирает наилучшую стратегию на основе возможностей модели
* **`None` **: Структурированный вывод явно не запрашивается

Когда тип схемы предоставляется напрямую, LangChain автоматически выбирает:

* `ProviderStrategy`, если выбранная модель и провайдер поддерживают собственный структурированный вывод (например, [OpenAI](/oss/python/integrations/providers/openai), [Anthropic (Claude)](/oss/python/integrations/providers/anthropic) или [xAI (Grok)](/oss/python/integrations/providers/xai)).
* `ToolStrategy` для всех остальных моделей.

<Note>

 Поддержка собственных функций структурированного вывода считывается динамически из модели [profile data](/oss/python/langchain/models#model-profiles), если используется `langchain>=1.1`. Если данные недоступны, используйте другое условие или укажите вручную:

 ```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  custom_profile = {
      "structured_output": True,
      # ...
  }
  model = init_chat_model("...", profile=custom_profile)
 ```

 Если указаны инструменты, модель должна поддерживать одновременное использование инструментов и структурированный вывод.
</Note>

Структурированный ответ возвращается в ключе `structured_response` конечного состояния агента.

## Стратегия провайдера

Некоторые провайдеры моделей изначально поддерживают структурированный вывод через свои API (например, OpenAI, xAI (Grok), Gemini, Anthropic (Claude)). Это самый надежный метод, если он доступен.

Чтобы использовать эту стратегию, настройте `ProviderStrategy`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
class ProviderStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    strict: bool | None = None
```

<Info>

 Для параметра `strict` требуется `langchain>=1.2`.
</Info>

<ParamField path="schema" required>

 Схема, определяющая структурированный формат вывода. Поддерживает:

 * **Pydantic models**: подклассы `BaseModel` с валидацией полей. Возвращает проверенный экземпляр Pydantic.
 * **Dataclasses**: классы данных Python с аннотациями типов. Возвращает словарь.
 * **TypedDict**: типизированные классы словарей. Возвращает словарь.
 * **JSON Schema**: словарь со спецификацией схемы JSON. Возвращает dict.
</ParamField>

<ParamField path="strict">

 Необязательный логический параметр для обеспечения строгого соблюдения схемы. Поддерживается некоторыми провайдерами (например, [OpenAI](/oss/python/интеграции/чат/openai) и [xAI](/oss/python/интеграции/ чат/xai)). По умолчанию установлено значение `None` (отключено).
</ParamField>

LangChain автоматически использует `ProviderStrategy`, когда вы передаете тип схемы напрямую в [`create_agent.response_format`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) и модель поддерживает собственный структурированный вывод:

<CodeGroup>
  ```python Pydantic Model theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from pydantic import BaseModel, Field
  from langchain.agents import create_agent


  class ContactInfo(BaseModel):
      """Contact information for a person."""
      name: str = Field(description="The name of the person")
      email: str = Field(description="The email address of the person")
      phone: str = Field(description="The phone number of the person")

  agent = create_agent(
      model="gpt-5",
      response_format=ContactInfo  # Auto-selects ProviderStrategy
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
  })

  print(result["structured_response"])
  # ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
  ```

  ```python Dataclass theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from dataclasses import dataclass
  from langchain.agents import create_agent


  @dataclass
  class ContactInfo:
      """Contact information for a person."""
      name: str # The name of the person
      email: str # The email address of the person
      phone: str # The phone number of the person

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ContactInfo  # Auto-selects ProviderStrategy
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
  })

  result["structured_response"]
  # {'name': 'John Doe', 'email': 'john@example.com', 'phone': '(555) 123-4567'}
  ```

  ```python TypedDict theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from typing_extensions import TypedDict
  from langchain.agents import create_agent


  class ContactInfo(TypedDict):
      """Contact information for a person."""
      name: str # The name of the person
      email: str # The email address of the person
      phone: str # The phone number of the person

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ContactInfo  # Auto-selects ProviderStrategy
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
  })

  result["structured_response"]
  # {'name': 'John Doe', 'email': 'john@example.com', 'phone': '(555) 123-4567'}
  ```

  ```python JSON Schema theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from langchain.agents import create_agent


  contact_info_schema = {
      "type": "object",
      "description": "Contact information for a person.",
      "properties": {
          "name": {"type": "string", "description": "The name of the person"},
          "email": {"type": "string", "description": "The email address of the person"},
          "phone": {"type": "string", "description": "The phone number of the person"}
      },
      "required": ["name", "email", "phone"]
  }

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ProviderStrategy(contact_info_schema)
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
  })

  result["structured_response"]
  # {'name': 'John Doe', 'email': 'john@example.com', 'phone': '(555) 123-4567'}
  ```
</CodeGroup>

Собственные структурированные выходные данные поставщика обеспечивают высокую надежность и строгую проверку, поскольку поставщик модели обеспечивает соблюдение схемы. Используйте ее, когда она доступна.

<Note>

 Если провайдер изначально поддерживает структурированный вывод для выбранной вами модели, то функционально это эквивалентно написанию `response_format=ProductReview` вместо `response_format=ProviderStrategy(ProductReview)`.

 В любом случае, если структурированный вывод не поддерживается, агент вернется к стратегии вызова инструмента.
</Note>

## Стратегия вызова инструмента

Для моделей, которые не поддерживают структурированный вывод, LangChain использует вызов инструмента для достижения того же результата. Это работает со всеми моделями, поддерживающими вызов инструментов (большинство современных моделей).

Чтобы использовать эту стратегию, настройте `ToolStrategy`:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
class ToolStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    tool_message_content: str | None
    handle_errors: Union[
        bool,
        str,
        type[Exception],
        tuple[type[Exception], ...],
        Callable[[Exception], str],
    ]
```

<ParamField path="schema" required>

 Схема, определяющая структурированный формат вывода. Поддерживает:

  * **Pydantic models**: подклассы `BaseModel` с валидацией полей. Возвращает проверенный экземпляр Pydantic.
  * **Dataclasses**: классы данных Python с аннотациями типов. Возвращает словарь.
  * **TypedDict**: типизированные словарные классы. Возвращает словарь.
  * **JSON Schema**: словарь со спецификацией схемы JSON. Возвращает словарь.
  * **Union types**: несколько вариантов схемы. Модель выберет наиболее подходящую схему в зависимости от контекста.
</ParamField>

<ParamField path="tool_message_content">

 Пользовательское содержимое для сообщения инструмента, возвращаемого при создании структурированного вывода.
 Если не указано, по умолчанию отображается сообщение со структурированными данными ответа.
</ParamField>

<ParamField path="handle_errors">
 Стратегия обработки ошибок при сбоях проверки структурированных выходных данных. По умолчанию используется значение True.

 * **`True` **: фиксирует все ошибки с помощью шаблона ошибок по умолчанию
 * **`str` * *: фиксирует все ошибки с помощью этого пользовательского сообщения
 * **`type[Exception]` **: перехватывать только этот тип исключения с сообщением по умолчанию
 * **`tuple[type[Exception], ...]` **: перехватывать только эти типы исключений с сообщением по умолчанию
 * **`Callable[[Exception], str]`**: Пользовательская функция, возвращающая сообщение об ошибке
 * **`False`**: никаких повторных попыток, разрешите исключениям распространяться
</ParamField>

<CodeGroup>
  ```python Pydantic Model theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from pydantic import BaseModel, Field
  from typing import Literal
  from langchain.agents import create_agent
  from langchain.agents.structured_output import ToolStrategy


  class ProductReview(BaseModel):
      """Analysis of a product review."""
      rating: int | None = Field(description="The rating of the product", ge=1, le=5)
      sentiment: Literal["positive", "negative"] = Field(description="The sentiment of the review")
      key_points: list[str] = Field(description="The key points of the review. Lowercase, 1-3 words each.")

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ToolStrategy(ProductReview)
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
  })
  result["structured_response"]
  # ProductReview(rating=5, sentiment='positive', key_points=['fast shipping', 'expensive'])
  ```

  ```python Dataclass theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from dataclasses import dataclass
  from typing import Literal
  from langchain.agents import create_agent
  from langchain.agents.structured_output import ToolStrategy


  @dataclass
  class ProductReview:
      """Analysis of a product review."""
      rating: int | None  # The rating of the product (1-5)
      sentiment: Literal["positive", "negative"]  # The sentiment of the review
      key_points: list[str]  # The key points of the review

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ToolStrategy(ProductReview)
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
  })
  result["structured_response"]
  # {'rating': 5, 'sentiment': 'positive', 'key_points': ['fast shipping', 'expensive']}
  ```

  ```python TypedDict theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from typing import Literal
  from typing_extensions import TypedDict
  from langchain.agents import create_agent
  from langchain.agents.structured_output import ToolStrategy


  class ProductReview(TypedDict):
      """Analysis of a product review."""
      rating: int | None  # The rating of the product (1-5)
      sentiment: Literal["positive", "negative"]  # The sentiment of the review
      key_points: list[str]  # The key points of the review

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ToolStrategy(ProductReview)
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
  })
  result["structured_response"]
  # {'rating': 5, 'sentiment': 'positive', 'key_points': ['fast shipping', 'expensive']}
  ```

  ```python JSON Schema theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from langchain.agents import create_agent
  from langchain.agents.structured_output import ToolStrategy


  product_review_schema = {
      "type": "object",
      "description": "Analysis of a product review.",
      "properties": {
          "rating": {
              "type": ["integer", "null"],
              "description": "The rating of the product (1-5)",
              "minimum": 1,
              "maximum": 5
          },
          "sentiment": {
              "type": "string",
              "enum": ["positive", "negative"],
              "description": "The sentiment of the review"
          },
          "key_points": {
              "type": "array",
              "items": {"type": "string"},
              "description": "The key points of the review"
          }
      },
      "required": ["sentiment", "key_points"]
  }

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ToolStrategy(product_review_schema)
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
  })
  result["structured_response"]
  # {'rating': 5, 'sentiment': 'positive', 'key_points': ['fast shipping', 'expensive']}
  ```

  ```python Union Types theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from pydantic import BaseModel, Field
  from typing import Literal, Union
  from langchain.agents import create_agent
  from langchain.agents.structured_output import ToolStrategy


  class ProductReview(BaseModel):
      """Analysis of a product review."""
      rating: int | None = Field(description="The rating of the product", ge=1, le=5)
      sentiment: Literal["positive", "negative"] = Field(description="The sentiment of the review")
      key_points: list[str] = Field(description="The key points of the review. Lowercase, 1-3 words each.")

  class CustomerComplaint(BaseModel):
      """A customer complaint about a product or service."""
      issue_type: Literal["product", "service", "shipping", "billing"] = Field(description="The type of issue")
      severity: Literal["low", "medium", "high"] = Field(description="The severity of the complaint")
      description: str = Field(description="Brief description of the complaint")

  agent = create_agent(
      model="gpt-5",
      tools=tools,
      response_format=ToolStrategy(Union[ProductReview, CustomerComplaint])
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
  })
  result["structured_response"]
  # ProductReview(rating=5, sentiment='positive', key_points=['fast shipping', 'expensive'])
  ```
</CodeGroup>

### Содержимое сообщения пользовательского инструмента

Параметр `tool_message_content` позволяет настроить сообщение, которое появляется в истории переписки при создании структурированного вывода:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


class MeetingAction(BaseModel):
    """Action items extracted from a meeting transcript."""
    task: str = Field(description="The specific task to be completed")
    assignee: str = Field(description="Person responsible for the task")
    priority: Literal["low", "medium", "high"] = Field(description="Priority level")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(
        schema=MeetingAction,
        tool_message_content="Action item captured and added to meeting notes!"
    )
)

agent.invoke({
    "messages": [{"role": "user", "content": "From our meeting: Sarah needs to update the project timeline as soon as possible"}]
})
```

```
================================ Human Message =================================

From our meeting: Sarah needs to update the project timeline as soon as possible
================================== Ai Message ==================================
Tool Calls:
  MeetingAction (call_1)
 Call ID: call_1
  Args:
    task: Update the project timeline
    assignee: Sarah
    priority: high
================================= Tool Message =================================
Name: MeetingAction

Action item captured and added to meeting notes!
```

Without `tool_message_content`, our final [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) would be:

```
================================= Tool Message =================================
Name: MeetingAction

Returning structured response: {'task': 'update the project timeline', 'assignee': 'Sarah', 'priority': 'high'}
```

### Обработка ошибок

Модели могут допускать ошибки при генерации структурированных выходных данных с помощью вызова инструмента. LangChain предоставляет интеллектуальные механизмы повторных попыток для автоматической обработки этих ошибок.

#### Ошибка множественных структурированных выходных данных

Если модель неправильно вызывает несколько инструментов для структурированного вывода, агент выдает сообщение об ошибке в виде [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage) и предлагает модели повторить попытку:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from pydantic import BaseModel, Field
from typing import Union
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


class ContactInfo(BaseModel):
    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")

class EventDetails(BaseModel):
    event_name: str = Field(description="Name of the event")
    date: str = Field(description="Event date")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(Union[ContactInfo, EventDetails])  # Default: handle_errors=True
)

agent.invoke({
    "messages": [{"role": "user", "content": "Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th"}]
})
```

```
================================ Human Message =================================

Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th
None
================================== Ai Message ==================================
Tool Calls:
  ContactInfo (call_1)
 Call ID: call_1
  Args:
    name: John Doe
    email: john@email.com
  EventDetails (call_2)
 Call ID: call_2
  Args:
    event_name: Tech Conference
    date: March 15th
================================= Tool Message =================================
Name: ContactInfo

Error: Model incorrectly returned multiple structured responses (ContactInfo, EventDetails) when only one is expected.
 Please fix your mistakes.
================================= Tool Message =================================
Name: EventDetails

Error: Model incorrectly returned multiple structured responses (ContactInfo, EventDetails) when only one is expected.
 Please fix your mistakes.
================================== Ai Message ==================================
Tool Calls:
  ContactInfo (call_3)
 Call ID: call_3
  Args:
    name: John Doe
    email: john@email.com
================================= Tool Message =================================
Name: ContactInfo

Returning structured response: {'name': 'John Doe', 'email': 'john@email.com'}
```

#### Ошибка проверки схемы

Когда структурированный вывод не соответствует ожидаемой схеме, агент предоставляет специальную обратную связь об ошибке:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


class ProductRating(BaseModel):
    rating: int | None = Field(description="Rating from 1-5", ge=1, le=5)
    comment: str = Field(description="Review comment")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(ProductRating),  # Default: handle_errors=True
    system_prompt="You are a helpful assistant that parses product reviews. Do not make any field or value up."
)

agent.invoke({
    "messages": [{"role": "user", "content": "Parse this: Amazing product, 10/10!"}]
})
```

```
================================ Human Message =================================

Parse this: Amazing product, 10/10!
================================== Ai Message ==================================
Tool Calls:
  ProductRating (call_1)
 Call ID: call_1
  Args:
    rating: 10
    comment: Amazing product
================================= Tool Message =================================
Name: ProductRating

Error: Failed to parse structured output for tool 'ProductRating': 1 validation error for ProductRating.rating
  Input should be less than or equal to 5 [type=less_than_equal, input_value=10, input_type=int].
 Please fix your mistakes.
================================== Ai Message ==================================
Tool Calls:
  ProductRating (call_2)
 Call ID: call_2
  Args:
    rating: 5
    comment: Amazing product
================================= Tool Message =================================
Name: ProductRating

Returning structured response: {'rating': 5, 'comment': 'Amazing product'}
```

#### Стратегии обработки ошибок

Вы можете настроить способ обработки ошибок, используя параметр `handle_errors`:

** Пользовательское сообщение об ошибке:**

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
ToolStrategy(
    schema=ProductRating,
    handle_errors="Please provide a valid rating between 1-5 and include a comment."
)
```

Если `handle_errors` — это строка, агент *всегда* будет предлагать модели повторить попытку с фиксированным сообщением:

```
================================= Tool Message =================================
Name: ProductRating

Please provide a valid rating between 1-5 and include a comment.
```

**Обрабатывайте только определенные исключения:**

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
ToolStrategy(
    schema=ProductRating,
    handle_errors=ValueError  # Only retry on ValueError, raise others
)
```

Если `handle_errors` — это тип исключения, агент будет повторять попытку (используя сообщение об ошибке по умолчанию) только в том случае, если возникшее исключение относится к указанному типу. Во всех остальных случаях будет возникать исключение.

 **Обработка нескольких типов исключений:**

 ```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
ToolStrategy(
    schema=ProductRating,
    handle_errors=(ValueError, TypeError)  # Retry on ValueError and TypeError
)
```

Если `handle_errors` представляет собой кортеж исключений, агент повторит попытку (используя сообщение об ошибке по умолчанию) только в том случае, если возникшее исключение относится к одному из указанных типов. Во всех остальных случаях будет сгенерировано исключение.

**Пользовательская функция обработки ошибок:**

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}

from langchain.agents.structured_output import StructuredOutputValidationError
from langchain.agents.structured_output import MultipleStructuredOutputsError

def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "There was an issue with the format. Try again."
    elif isinstance(error, MultipleStructuredOutputsError):
        return "Multiple structured outputs were returned. Pick the most relevant one."
    else:
        return f"Error: {str(error)}"


agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(
                        schema=Union[ContactInfo, EventDetails],
                        handle_errors=custom_error_handler
                    )  # Default: handle_errors=True
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th"}]
})

for msg in result['messages']:
    # If message is actually a ToolMessage object (not a dict), check its class name
    if type(msg).__name__ == "ToolMessage":
        print(msg.content)
    # If message is a dictionary or you want a fallback
    elif isinstance(msg, dict) and msg.get('tool_call_id'):
        print(msg['content'])

```

В случае ошибки `StructuredOutputValidationError`:

```
================================= Tool Message =================================
Name: ToolStrategy

There was an issue with the format. Try again.
```

При возникновении ошибки `MultipleStructuredOutputsError`:

```
================================= Tool Message =================================
Name: ToolStrategy

Multiple structured outputs were returned. Pick the most relevant one.
```

При возникновении других ошибок:

```
================================= Tool Message =================================
Name: ToolStrategy

Error: <error message>
```

**Обработка ошибок не предусмотрена:**

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
response_format = ToolStrategy(
    schema=ProductRating,
    handle_errors=False  # All errors raised
)
```
