# Запускается - streamlit run UI.py

import streamlit as st
from temp import agent


st.set_page_config(page_title="AI Research Agent", layout="centered")

st.title("🔎 AI Research Agent")

# Инициализация истории
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
user_input = st.chat_input("Задай вопрос...")

if user_input:
    # Добавляем сообщение пользователя
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Ответ агента
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                response = agent.invoke({"input": user_input})

                # если агент возвращает сложный объект
                if isinstance(response, dict):
                    response_text = response.get("output", str(response))
                else:
                    response_text = str(response)

            except Exception as e:
                response_text = f"Ошибка: {e}"

        st.markdown(response_text)

    # Сохраняем ответ
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })