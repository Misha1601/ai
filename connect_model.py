from models import MODEL_Y1
from langchain_core.messages import HumanMessage

print("🔄 Отправляю тестовый запрос...")
response = MODEL_Y1.invoke([HumanMessage(content="Ответь одним словом: тест")])
print(response.content)
