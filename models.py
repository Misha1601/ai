from settings import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL, BASE_URL

from agents import Agent, Runner
from openai import OpenAI, AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage


MODEL_Y1 = ChatOpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url=BASE_URL,
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        temperature=0.5
    )

MODEL_Q36 = ChatOpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url=BASE_URL,
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/qwen3.6-35b-a3b/latest",
        temperature=0
    )

# YANDEX = ChatYandexGPT(
#         api_key=YANDEX_CLOUD_API_KEY,
#         folder_id=YANDEX_CLOUD_FOLDER
#     )



# agent = create_agent(
#     model=MODEL_Y1
# )


# answer = MODEL_Y1.invoke(
#     [
#         SystemMessage(
#             content="Вы — полезный помощник, отвечаю на вопросы по Python."
#         ),
#         HumanMessage(content="Я люблю программировать."),
#     ]
# )

# print(answer.content)

agent = create_agent(
    model=MODEL_Y1
)

# response = agent.invoke({
#                 "messages": [{
#                     "role": "user",
#                     "content": f"Кто ты?"
#                 }]
#             })
# print(response)
# result = response["messages"][-1].content_blocks
# result = response["messages"]
# for res in result:
#     print(res.content)
# print(result)


# === OpenAI-compatible client ===
client = OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url=BASE_URL,
)

# response = client.responses.create(
#     model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
#     input="Какая столица России?"
# )

# print(response.output_text)


client = AsyncOpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url=BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
    openai_client=client,
)

# agent = Agent(
#     name="Репетитор по истории",
#     instructions="Вы четко и лаконично отвечаете на вопросы по истории.",
#     model=model,
# )

# result = Runner.run_sync(agent, "Когда пала Римская империя?")
# print(result.final_output)