from settings import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL, BASE_URL
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.tools import tool



madel = ChatOpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url=BASE_URL,
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        temperature=0
    )

