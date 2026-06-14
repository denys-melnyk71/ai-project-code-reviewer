import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError
import streamlit as st
from reviewer.schemas import ReviewResult

# Системна інструкція, що задає роль та правила поведінки для моделі
SENIOR_DEV_INSTRUCTION = """
Ти — досвідчений Senior Python Developer та Tech Lead. Твоє завдання — провести ретельний код-рев'ю наданого Python-коду.
Аналізуй код за такими критеріями:
1. Відповідність стандартам PEP 8.
2. Потенційні вразливості та проблеми безпеки (наприклад, SQL-ін'єкції, hardcoded паролі, unsafe eval).
3. Можливості для рефакторингу, оптимізації та покращення читаємості (DRY, Clean Code).

Ти ПОВИНЕН повернути відповідь СУВОРO у форматі JSON, який відповідає заданій燬хемі структурованого виводу.
Усі описи, підсумки та рекомендації пиши виключно УКРАЇНСЬКОЮ мовою. Код у полі refactored_code має бути готовим до запуску та повністю виправленим.
"""

# Декоратор st.cache_data автоматично аналізує code_content.
# Якщо один і той самий код відправляти декілька разів, результат миттєво повернеться з локального кешу.
@st.cache_data(show_spinner=False)
def _get_api_response(code_content: str) -> str:
    """
    Внутрішня функція для отримання сирої відповіді від API. Закешована через Streamlit.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API-ключ 'GEMINI_API_KEY' не знайдено в змінних оточення!")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=code_content,
            config=types.GenerateContentConfig(
                system_instruction=SENIOR_DEV_INSTRUCTION,
                temperature=0.2,
                top_p=0.95,
                response_mime_type="application/json",
                response_schema=ReviewResult,
            ),
        )
        return response.text

    except APIError as e:
        if e.code == 429:
            raise RuntimeError("Перевищено ліміти безкоштовних запитів (Resource Exhausted). Спробуйте пізніше.")
        elif e.code == 400:
            raise RuntimeError("Неправильний запит або невалідний формат даних (InvalidArgument).")
        elif e.code == 403:
            raise RuntimeError("Помилка автентифікації. Перевірте ваш GEMINI_API_KEY.")
        else:
            raise RuntimeError(f"Помилка Gemini API: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Сталася непередбачувана помилка під час запиту до API: {str(e)}")


def analyze_code(code_content: str) -> ReviewResult:
    """
    Основна функція, яка викликає закешований запит і валідує результат через Pydantic.
    """
    # Отримуємо JSON-рядок (з кешу або від API)
    raw_json = _get_api_response(code_content)
    
    try:
        return ReviewResult.model_validate_json(raw_json)
    except ValidationError as e:
        raise RuntimeError(f"Помилка валідації відповіді API: {e}") from e