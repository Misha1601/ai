import streamlit as st
from langchain_openai import ChatOpenAI

# твой агент
from models import agent

st.title("AI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ввод пользователя
user_input = st.chat_input("Напиши что-нибудь")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # ответ агента
    result = agent.invoke({
    "messages": [{"role": "user", "content": user_input}]
    })

    response = result["messages"][-1].content

    st.session_state.messages.append({"role": "assistant", "content": response})

# вывод истории
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])