import json
from pathlib import Path
from langchain.tools import tool

MEMORY_PATH = Path(__file__).parent / "memory.json"


def _load_memory() -> dict:
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(data: dict) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@tool
def read_memory(key: str = "all") -> str:
    """
    Читает данные из memory.json.
    key="all"              — возвращает весь файл
    key="user_profile"    — только профиль пользователя
    key="pending_questions"  — список оставшихся вопросов
    key="onboarding_complete" — статус онбординга (bool)
    """
    data = _load_memory()
    if key == "all":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return json.dumps(data.get(key), ensure_ascii=False, indent=2)


@tool
def write_memory(field: str, value: str) -> str:
    """
    Сохраняет ответ пользователя в user_profile и удаляет
    соответствующий вопрос из pending_questions.

    field — идентификатор поля (например "name", "age", "agent_purpose")
    value — значение, полученное от пользователя
    """
    data = _load_memory()

    # Сохраняем ответ в профиль
    data["user_profile"][field] = value

    # Удаляем вопрос из очереди
    data["pending_questions"] = [
        q for q in data["pending_questions"] if q["field"] != field
    ]

    # Проверяем завершённость онбординга
    if not data["pending_questions"]:
        data["onboarding_complete"] = True

    _save_memory(data)

    remaining = len(data["pending_questions"])
    status = "Онбординг завершён!" if data["onboarding_complete"] else f"Осталось вопросов: {remaining}"
    return f"Сохранено: {field} = {value}. {status}"