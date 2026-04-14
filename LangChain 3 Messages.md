# Сообщения

Сообщения — это основная единица контекста для моделей в LangChain. Они представляют собой входные и выходные данные моделей, содержащие как контент, так и метаданные, необходимые для отображения состояния диалога при взаимодействии с большой языковой моделью.

Сообщения — это объекты, которые содержат:

* **Роль** — определяет тип сообщения (например, `system`, `user`)
* **Содержимое** — фактическое содержимое сообщения (текст, изображения, аудио, документы и т. д.).
* **Метаданные** — дополнительные поля, такие как информация об ответе, идентификаторы сообщений и использование токенов

LangChain предоставляет стандартный тип сообщения, который работает во всех поставщиках моделей, обеспечивая согласованное поведение независимо от вызываемой модели.

## Базовое использование

Самый простой способ использовать messages - это создавать объекты message и передавать их модели при вызове.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

model = init_chat_model("gpt-5-nano")

system_msg = SystemMessage("Ты очень полезный помощник.")
human_msg = HumanMessage("Привет, как дела?")

# Используйте с моделями чата
messages = [system_msg, human_msg]
response = model.invoke(messages) # Возвращает AIMessage
```

### Текстовые подсказки

Текстовые подсказки — это строки, которые идеально подходят для простых задач генерации, когда не нужно сохранять историю диалога.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
response = model.invoke("Напишите хайку о весне")
```

**Используйте текстовые подсказки, когда:**

* У вас один отдельный запрос
* Вам не нужна история переписки
* Вы хотите свести к минимуму сложность кода

### Подсказки для сообщений

Кроме того, вы можете передать модели список сообщений, предоставив список объектов сообщений.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("Вы знаток поэзии"),
    HumanMessage("Напишите хайку о весне"),
    AIMessage("Цветут сакуры...")
]
response = model.invoke(messages)
```

**Используйте подсказки для сообщений, когда:**

* ведете многоэтапный диалог
* работаете с мультимодальным контентом (изображениями, аудио, файлами)
* включаете системные инструкции

### Формат словаря

Вы также можете указать сообщения непосредственно в формате подсказок для чата OpenAI.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
messages = [
    {"role": "system", "content": "Вы разбираетесь в поэзии"},
    {"role": "user", "content": "Напишите хайку о весне"},
    {"role": "assistant", "content": "Цветут сакуры..."}
]
response = model.invoke(messages)
```

## Типы сообщений

* Системное сообщение (#system-message) - сообщает модели, как вести себя, и предоставляет контекст для взаимодействий.
* Человеческое сообщение (#human-message) - представляет ввод данных пользователем и взаимодействие с моделью.
* Сообщение от ИИ (#ai-message) — ответы, сгенерированные моделью, включая текстовое содержимое, вызовы инструментов и метаданные
* Сообщение от инструмента (#tool-message) — представляет результаты вызовов инструментов

### Системное сообщение

`SystemMessage` представляет собой начальный набор инструкций, определяющих поведение модели. С помощью системного сообщения можно задать тон, определить роль модели и установить правила реагирования.

Основные инструкции
```python
system_msg = SystemMessage("Вы — полезный помощник в написании кода.")
messages = [
    system_msg,
    HumanMessage("Как создать REST API?")
]
response = model.invoke(messages)
```

Детализированный образ
```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import SystemMessage, HumanMessage

system_msg = SystemMessage("""
    Вы — старший разработчик на Python с опытом работы с веб-фреймворками.
    Всегда приводите примеры кода и объясняйте свои действия.
    Будьте краткими, но исчерпывающими в своих объяснениях.
    """)

messages = [
    system_msg,
    HumanMessage("Как создать REST API?")
]
response = model.invoke(messages)
```

***

### Сообщение от пользователя

`HumanMessage` представляет пользовательский ввод и взаимодействия. Они могут содержать текст, изображения, аудио, файлы и любое другое количество мультимодального [контента] (#message-content).

#### Текстовое содержимое
Объект сообщения
```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
response = model.invoke([
    HumanMessage("Что такое машинное обучение?")
])
```
Использование строки
```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
response = model.invoke("Что такое машинное обучение?")
```

#### Метаданные сообщения

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
human_msg = HumanMessage(
    content="Привет!",
    name="alice", # Необязательно: укажите разных пользователей
    id="msg_123", # Необязательно: уникальный идентификатор для отслеживания
)
```

Поведение поля `name` зависит от поставщика — некоторые используют его для идентификации пользователя, другие игнорируют. Чтобы проверить, обратитесь к поставщику модели [ссылка] (https://reference.langchain.com/python/integrations/).


***

### Сообщение AI

[`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage) представляет выходные данные вызова модели. Они могут включать в себя мультимодальные данные, вызовы инструментов и метаданные поставщика, к которым вы сможете получить доступ позже.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
response = model.invoke("Explain AI")
print(type(response)) # <class 'langchain.messages.AIMessage'>
```

[`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage) — это объект, возвращаемый моделью при вызове и содержащий все связанные метаданные в ответе.

Провайдеры по-разному оценивают и интерпретируют типы сообщений, поэтому иногда бывает полезно вручную создать новый объект [`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage) и вставить его в историю сообщений, как если бы оно было создано моделью.

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import AIMessage, SystemMessage, HumanMessage

# Создайте сообщение с искусственным интеллектом вручную (например, для истории переписки)
ai_msg = AIMessage("Я буду рад помочь вам с этим вопросом!")

# Добавить в историю переписки
messages = [
 SystemMessage("Ты очень полезный помощник"),
 HumanMessage("Можешь мне помочь?"),
 ai_msg, # Вставить так, как будто оно пришло от модели
 HumanMessage("Отлично! Сколько будет 2+2?")
]

response = model.invoke(messages)
```

<Accordion title="Атрибуты">
 <ParamField path="text" type="string">
 Текстовое содержимое сообщения.
 </ParamField>

 <ParamField path="content" type="string | dict[]">
 Исходное содержимое сообщения.
 </ParamField>

 <ParamField path="content_blocks" type="ContentBlock[]">
 Стандартизированные [блоки контента](#message-content) сообщения.
 </ParamField>
 <ParamField path="tool_calls" type="dict[] | None">
 Вызовы инструментов, выполненные моделью.

 Пустое значение, если инструменты не вызывались.
 </ParamField>

 <Путь к ParamField="id" тип="строка">
 Уникальный идентификатор сообщения (автоматически генерируется LangChain или возвращается в ответе провайдера)
 </ParamField>
 <ParamField path="usage_metadata" type="dict | None">
 Метаданные об использовании сообщения, которые могут содержать количество токенов, если таковые имеются.
 </ParamField>

 <ParamField path="response_metadata" type="ResponseMetadata | None">
 Метаданные ответа сообщения.
 </ParamField>
</Accordion>

#### Вызовы инструмента

Когда модели выполняют [вызовы инструментов](/oss/python/langchain/models#tool-calling), они включаются в [`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage):

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")

def get_weather(location: str) -> str:
     """Узнайте погоду в указанном месте."""
    ...

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("Какая погода в Париже?")

for tool_call in response.tool_calls:
    print(f"Инструмент: {tool_call['name']}")
    print(f"Аргументы: {tool_call['args']}")
    print(f"Идентификатор: {tool_call['id']}")
```

Другие структурированные данные, такие как рассуждения или цитаты, также могут отображаться в содержимом сообщении.

#### Использование токена

[`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage ) может содержать количество токенов и другие метаданные использования в своем [`usage_metadata`](https://reference.langchain.com/python/langchain-core/messages/ai/UsageMetadata ) поле:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")

response = model.invoke("Hello!")
response.usage_metadata
```

```
{'input_tokens': 8,
 'output_tokens': 304,
 'total_tokens': 312,
 'input_token_details': {'audio': 0, 'cache_read': 0},
 'output_token_details': {'audio': 0, 'reasoning': 256}}
```

Смотрите [`UsageMetadata`](https://reference.langchain.com/python/langchain-core/messages/ai/UsageMetadata) для получения подробной информации.

#### Потоковая передача и фрагменты

Во время потоковой передачи вы будете получать [`AIMessageChunk`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessageChunk) объекты, которые можно объединить в полноценный объект сообщения:

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
chunks = []
full_message = None
for chunk in model.stream("Привет"):
    chunks.append(chunk)
    print(chunk.text)
    full_message = chunk if full_message is None else full_message + chunk
```

<Note>
 Подробнее:

 * [Потоковая передача токенов из чат-моделей](/oss/python/langchain/models#stream)
 * [Потоковая передача токенов и/или шагов от агентов](/oss/python/langchain/streaming)
</Note>

***

### Сообщение от инструмента

Для моделей, поддерживающих [вызов инструментов](/oss/python/langchain/models#tool-calling), сообщения ИИ могут содержать вызовы инструментов. Сообщения инструментов используются для передачи результатов выполнения одного инструмента в модель.

[Инструменты](/oss/python/langchain/tools) могут напрямую генерировать объекты [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage). Ниже приведен простой пример. Подробнее читайте в [руководстве по инструментам](/oss/python/langchain/tools).

```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
from langchain.messages import AIMessage
from langchain.messages import ToolMessage

# После того как модель вызывает инструмент
# (Здесь мы для краткости демонстрируем создание сообщений вручную)
ai_message = AIMessage(
 content=[],
 tool_calls=[{
 "name": "get_weather",
 "args": {"location": "Сан-Франциско"},
 "id": "call_123"
 }]
)

# Запустить инструмент и создать сообщение с результатом
weather_result = "Солнечно, 22 °C"
tool_message = ToolMessage(
 content=weather_result,
 tool_call_id="call_123" # Должно совпадать с идентификатором вызова
)

# Продолжить диалог
messages = [
 HumanMessage("Какая погода в Сан-Франциско?"),
 ai_message, # Вызов инструмента модели
 tool_message, # Результат выполнения инструмента
]
response = model.invoke(messages) # Модель обрабатывает результат
```

<Accordion title="Attributes">
 <ParamField path="content" type="string" required>
 Строковый вывод вызова инструмента.
 </ParamField>

 <ParamField path="tool_call_id" type="string" required>
 Идентификатор вызова инструмента, на который отвечает это сообщение. Должен совпадать с идентификатором вызова инструмента в [`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage).
 </ParamField>

 <ParamField path="name" type="string" required>
 Название вызванного инструмента.
 </ParamField>

 <ParamField path="artifact" type="dict">
 Дополнительные данные не отправляются в модель, но к ним можно получить программный доступ.
 </ParamField>
</Accordion>

<Note>

 В поле `artifact` хранятся дополнительные данные, которые не будут отправлены в модель, но к которым можно получить программный доступ. Это удобно для хранения необработанных результатов, отладочной информации или данных для последующей обработки, не загромождая контекст модели.

 <Accordion title="Пример: использование артефакта для извлечения метаданных">

  Например, инструмент [retrieval](/oss/python/langchain/retrieval) может извлечь отрывок из документа для использования в модели. Если сообщение `content` содержит текст, на который будет ссылаться модель, то `artifact` может содержать идентификаторы документов или другие метаданные, которые может использовать приложение (например, для отображения страницы). См. пример ниже:

  ```python theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
  from langchain.messages import ToolMessage

  # Отправляется в модель
  message_content = "Это были лучшие времена, и это были худшие времена".

  # Артефакт доступен ниже по потоку
  artifact = {"document_id": "doc_123", "page": 0}

  tool_message = ToolMessage(
      content=message_content,
      tool_call_id="call_123",
      name="search_books",
      artifact=artifact,
  )
  ```

  Смотрите [Руководство по RAG] (/oss/python/langchain/rag) для получения сквозного примера построения [agents] извлечения (/oss/python/langchain/agents) с помощью LangChain.
 </Accordion>
</Note>

***

## Содержимое сообщения

Содержимое сообщения можно представить как полезную нагрузку данных, отправляемую в модель. У сообщений есть атрибут `content`, который имеет слабую типизацию и поддерживает строки и списки нетипизированных объектов (например, словарей). Это позволяет напрямую использовать в чат-моделях LangChain структуры, характерные для провайдеров, такие как [мультимодальный](#multimodal) контент и другие данные.

Кроме того, LangChain предоставляет специальные типы контента для текста, пояснений, цитат, мультимодальных данных, вызовов серверных инструментов и других элементов сообщений.  См. [блоки контента](#standard-content-blocks) ниже.

Чат-модели LangChain принимают контент сообщений в атрибуте `content`.

Он может содержать:

1. Строку
2. Список блоков контента в формате, принятом у провайдера
3. Список [стандартных блоков контента LangChain](#standard-content-blocks)

Смотрите ниже пример использования входных данных [multimodal] (#мультимодальный):

```python theme={"тема":{"светлая": "катппучино-латте","темная": "катппучино-мокко"}}
from langchain.messages import HumanMessage

# Содержимое строки
human_message = HumanMessage("Привет, как дела?")

# Собственный формат провайдера (например, OpenAI)
human_message = HumanMessage(content=[
    {"type": "text", "text": "Привет, как дела?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
])

# Список стандартных блоков контента
human_message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Привет, как дела?"},
    {"type": "image", "url": "https://example.com/image.jpg"},
])
```

<Tip>

 Указание `content_blocks` при инициализации сообщения по-прежнему заполняет поле `content`, но обеспечивает для этого типобезопасный интерфейс.
</Tip>

### Стандартные блоки контента

LangChain предоставляет стандартное представление содержимого сообщений, которое работает во всех провайдерах.

Объекты сообщений реализуют свойство `content_blocks`, которое лениво преобразует атрибут content в стандартное, типобезопасное представление. Например, сообщения, сгенерированные с помощью [`ChatAnthropic`](/oss/python/integrations/chat/anthropic) или [`ChatOpenAI`](/oss/python/integrations/chat/openai), будут содержать блоки thinking или reasoning в формате соответствующего провайдера, но их можно лениво преобразовать в единое представление [`ReasoningContentBlock`](#content-block-reference):

Ознакомьтесь с [руководствами по интеграции](/oss/python/integrations/providers/overview), чтобы начать работу с выбранным вами провайдером логического вывода.


**Сериализация стандартного контента**
Если приложению за пределами LangChain нужен доступ к блоку стандартного контента
Чтобы сохранить блоки контента в содержимом сообщения, вы можете включить эту функцию.
Для этого установите для переменной среды `LC_OUTPUT_VERSION` значение `v1`. Или инициализируйте любую модель чата с помощью `output_version="v1"`


### Мультимодальность

**Мультимодальность** — это способность работать с данными в различных форматах, таких как текст, аудио, изображения и видео. LangChain включает в себя стандартные типы данных, которые можно использовать в разных провайдерах.

[Чат-модели](/oss/python/langchain/models) могут принимать мультимодальные данные в качестве входных и генерировать их в качестве выходных. Ниже приведены короткие примеры входных сообщений с мультимодальными данными.

Дополнительные ключи могут быть указаны на верхнем уровне блока контента или вложены в `"extras": {"key": value}`.

[OpenAI](/oss/python/integrations/chat/openai) и [AWS Bedrock Converse](/oss/python/integrations/chat/bedrock),
например, требуют указывать имя файла для PDF-файлов. См. [страницу провайдера](/oss/python/integrations/providers/overview) для выбранной вами модели.

Не все модели поддерживают все типы файлов. Проверьте [справочник] поставщика моделей (https://reference.langchain.com/python/integrations/) на предмет поддерживаемых форматов и ограничений по размеру.

### Ссылка на блок содержимого

Блоки контента представлены (при создании сообщения или обращении к свойству `content_blocks`) в виде списка типизированных словарей. Каждый элемент в списке должен соответствовать одному типу блоков.
Просмотрите определения канонических типов в [справочнике по API](https://reference.langchain.com/python/langchain/messages).

Блоки контента были добавлены в качестве нового свойства сообщений в LangChain версии 1, чтобы стандартизировать форматы контента для всех провайдеров, сохранив при этом обратную совместимость с существующим кодом.

Блоки содержимого не являются заменой свойства [`content`](https://reference.langchain.com/python/langchain-core/messages/base/BaseMessage), а скорее новым свойством, которое можно использовать для доступа к содержимому сообщения в стандартном формате.

## Использование с моделями чатов

[Чат-модели](/oss/python/langchain/models) принимают на вход последовательность объектов сообщений и возвращают на выходе [`AIMessage`](https://reference.langchain.com/python/langchain-core/messages/ai/AIMessage). Взаимодействие часто происходит без сохранения состояния, поэтому в простом цикле диалога модель вызывается с растущим списком сообщений.
