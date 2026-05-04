from settings import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL, BASE_URL
from langchain_openai import ChatOpenAI

from langchain_community.chat_models import ChatYandexGPT
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
        temperature=0.5
    )

YANDEX = ChatYandexGPT(
        api_key=YANDEX_CLOUD_API_KEY,
        folder_id=YANDEX_CLOUD_FOLDER
    )



agent = create_agent(
    model=MODEL_Y1
)


# answer = YANDEX.invoke(
#     [
#         SystemMessage(
#             content="Вы — полезный помощник, отвечаю на вопросы по Python."
#         ),
#         HumanMessage(content="Я люблю программировать."),
#     ]
# )

# answer