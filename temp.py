from models import MODEL_Y1, YANDEX
model = MODEL_Y1
# model = YANDEX

from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Показывает погоду в вашем городе"""
    return f"Сейчас в {location} 10 градусов тепла."

print(model.profile)
# Bind (potentially multiple) tools to the model
# model_with_tools = model.bind_tools([get_weather], tool_choice="get_weather")
# model_with_tools = model.bind_tools([get_weather], tool_choice="any")
model_with_tools = model.bind_tools([get_weather])
print(model.profile)

# Step 1: Model generates tool calls
messages = [{"role": "user", "content": "В Москве и Казани сегодня тепло?"}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# Step 2: Execute tools and collect results
for tool_call in ai_msg.tool_calls:
    # Execute the tool with the generated arguments
    print(tool_call)
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)
    print(tool_result)

# Step 3: Pass results back to model for final response
final_response = model_with_tools.invoke(messages)
print(final_response.text)
# print(type(model))
# print(dir(model))
model.invoke("Привет")
print(model.profile)

from langchain.messages import SystemMessage, HumanMessage, AIMessage
messages = [
 {"role": "system", "content": "Вы разбираетесь в поэзии"},
 {"role": "user", "content": "Напишите хайку о весне"},
 {"role": "assistant", "content": "Цветут сакуры..."}
]
response = model.invoke(messages)

print(response)



