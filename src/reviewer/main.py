import os
import sys
import streamlit as st

# Додаємо папку 'src' до шляхів пошуку модулів Python
current_dir = os.path.dirname(os.path.abspath(__file__))  # папка src/reviewer
src_dir = os.path.dirname(current_dir)                    # папка src
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from reviewer.core import analyze_code

# --- КОНСТАНТИ --- 
APP_TITLE = "AI Code Reviewer"
APP_ICON = "🤖"
APP_CAPTION = (
    "Автоматичний аналіз Python-коду на відповідність PEP 8, безпеку та рефакторинг "
    "з локальним кешуванням."
)
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
WARNING_NO_API_KEY = (
    f"⚠️ Змінну оточення {GEMINI_API_KEY_ENV_VAR} не знайдено. "
    "Переконайтеся, що ви налаштували її перед запуском."
)
SIDEBAR_HEADER = "⚙️ Налаштування застосунку"
CLEAR_CACHE_BUTTON_TEXT = "🧹 Очистити локальний кеш запитів"
CACHE_CLEARED_MESSAGE = "Кеш успішно очищено!"
INPUT_HEADER = "📝 Ваш Python код"
FILE_UPLOADER_LABEL = "Прикріпіть файл з кодом (.py)"
FILE_UPLOAD_SUCCESS = "📂 Файл **{file_name}** успішно завантажено!"
FILE_READ_ERROR = "Помилка при читанні файлу: {error_message}"
TEXT_AREA_LABEL = "Або вставте код для аналізу вручну:"
TEXT_AREA_PLACEHOLDER = "def my_function(x):\n    eval(x) # Приклад небезпечного коду"
SUBMIT_BUTTON_TEXT = "Запустити рев'ю"
RESULTS_HEADER = "📊 Результати аналізу"
EMPTY_INPUT_ERROR = "Будь ласка, введіть код або завантажте файл перед натисканням кнопки!"
SPINNER_MESSAGE = "Senior Developer аналізує ваш код..."
SCORE_SUMMARY_HEADER = "### Оцінка коду: :{color}[{score}/10]"
MENTOR_SUMMARY_TEXT = "**Резюме від ментора:** {summary}"
ISSUES_HEADER = "### 🔍 Знайдені проблеми"
NO_ISSUES_MESSAGE = "Чудова робота! Жодних проблем не виявлено."
REFACTORING_HEADER = "### 🛠️ Рекомендований рефакторинг коду"
INITIAL_INFO_MESSAGE = (
    "Очікування коду... Завантажте файл або вставте код вище та натисніть "
    "'Запустити рев'ю'."
)

# Налаштування сторінки Streamlit
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title(f"{APP_ICON} {APP_TITLE} (Senior Developer Role)")
st.caption(APP_CAPTION)

# Перевірка наявності API ключа в системі для відображення попередження користувачу
if GEMINI_API_KEY_ENV_VAR not in os.environ:
    st.warning(WARNING_NO_API_KEY)

# Бічна панель (Sidebar) для керування кешем
with st.sidebar:
    st.header(SIDEBAR_HEADER)
    if st.button(CLEAR_CACHE_BUTTON_TEXT, use_container_width=True):
        st.cache_data.clear()
        st.success(CACHE_CLEARED_MESSAGE)

# --- ВЕРХНЯ ЧАСТИНА: Введення коду ---
st.header(INPUT_HEADER)

# Додаємо віджет для завантаження файлу (дозволяємо лише розширення .py)
uploaded_file = st.file_uploader(FILE_UPLOADER_LABEL, type=["py"])

code_input = ""

# Перевіряємо, чи користувач прикріпив файл
if uploaded_file is not None:
    try:
        # Читаємо вміст файлу у вигляді тексту (текст коду зазвичай у кодуванні utf-8)
        code_input = uploaded_file.getvalue().decode("utf-8")
        st.success(FILE_UPLOAD_SUCCESS.format(file_name=uploaded_file.name))
        
        # Показуємо завантажений код у згорнутому виді, щоб він не займав багато місця
        with st.expander("Переглянути вміст завантаженого файлу"):
            st.code(code_input, language="python")
    except Exception as e:
        st.error(FILE_READ_ERROR.format(error_message=str(e)))
else:
    # Якщо файл не завантажено, показуємо стандартне текстове поле
    code_input = st.text_area(
        TEXT_AREA_LABEL, 
        height=250, 
        placeholder=TEXT_AREA_PLACEHOLDER
    )

submit_button = st.button(SUBMIT_BUTTON_TEXT, type="primary", use_container_width=True)

# Візуальний розділювач між введенням та результатом
st.markdown("---")

# --- НИЖНЯ ЧАСТИНА: Результати аналізу ---
st.header(RESULTS_HEADER)

if submit_button:
    if not code_input or not code_input.strip():
        st.error(EMPTY_INPUT_ERROR)
    else:
        with st.spinner(SPINNER_MESSAGE):
            try:
                # Виклик логіки аналізу (тепер захищений кешем)
                result = analyze_code(code_input)
                
                # Відображення загальної оцінки
                score_color = "green" if result.score >= 7 else "orange" if result.score >= 4 else "red"
                st.markdown(SCORE_SUMMARY_HEADER.format(color=score_color, score=result.score))
                
                st.markdown(MENTOR_SUMMARY_TEXT.format(summary=result.summary))
                
                # Відображення знайдених зауважень
                st.markdown(ISSUES_HEADER)
                if not result.issues:
                    st.success(NO_ISSUES_MESSAGE)
                else:
                    # Перетворюємо список Pydantic-моделей у формат для зручного виведення
                    issues_table = [{
                        'Категорія': issue.category, 
                        'Рядок': issue.line_number, 
                        'Опис': issue.description, 
                        'Рекомендація': issue.suggestion
                    } for issue in result.issues]
                    st.table(issues_table)
                
                # Відображення рефакторингу
                st.markdown(REFACTORING_HEADER)
                st.code(result.refactored_code, language="python")
                
            except Exception as e:
                # Показ помилки користувачеві у гарному вікні
                # Для UI-додатків загальний Exception часто прийнятний,
                # але для бекенду варто обробляти специфічні винятки.
                st.error(str(e))
else:
    st.info(INITIAL_INFO_MESSAGE)