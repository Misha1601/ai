# agent.py

from models import MODEL_Q36
from langchain.agents import create_agent

SYSTEM_PROMPT = """
Тебя зовут Сашка.
Ты проверяешь ответы пользователя на вопросы.
Отвечай только "да" или "нет".
"""

agent = create_agent(
    model=MODEL_Q36,
    system_prompt=SYSTEM_PROMPT
)

list_questions = [
    "Какой сегодня день?",
    "Какая погода сегодня?",
    "Что такое искусственный интеллект?"
]


def main():
    print("Ответь на вопросы. Напиши 'выход' для завершения.\n")

    remaining_questions = list_questions[:]

    while remaining_questions:
        for question in remaining_questions[:]:  # безопасная копия
            print(f"Агент: {question}")
            user_input = input("Вы: ").strip()

            if user_input.lower() in ["выход", "exit", "quit"]:
                print("Агент: Пока!")
                return

            # проверка ответа через модель
            response = agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Вопрос: {question}. Ответ пользователя: {user_input}. Ответ корректный? ответь только да или нет"
                }]
            })

            print(response)
            result = response["messages"][-1].content.lower()

            if "да" in result:
                print("Агент: Принято ✅\n")
                remaining_questions.remove(question)
            else:
                print("Агент: Попробуй ещё раз ❌\n")

    print("Агент: Все вопросы были успешно отвечены!")


if __name__ == "__main__":
    main()
