import os
import google.generativeai as genai
from config import PROGRAMS, INSTRUCTION_PROMPT

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 0.3,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config
)

def build_full_context():
    """Собирает весь контекст из файлов в одну большую строку."""
    context_parts = [INSTRUCTION_PROMPT]
    
    for prog_key, details in PROGRAMS.items():
        title = details['title']
        
        context_parts.append(f"\n\n{'='*20}\nИНФОРМАЦИЯ О ПРОГРАММЕ: {title}\n{'='*20}\n")
        try:
            context_parts.append(details['page_txt'].read_text(encoding='utf-8'))
        except FileNotFoundError:
            context_parts.append(f"[Файл {details['page_txt']} не найден. Запустите parsers.py]")

        context_parts.append(f"\n\n--- Учебный план программы: {title} ---\n")
        try:
            context_parts.append(details['plan_txt'].read_text(encoding='utf-8'))
        except FileNotFoundError:
            context_parts.append(f"[Файл {details['plan_txt']} не найден. Запустите parsers.py]")

    return "\n".join(context_parts)

FULL_CONTEXT = build_full_context()

def get_gemini_response(question: str, history: list) -> str:
    """
    Отправляет запрос в Gemini и возвращает ответ.
    `history` - это список словарей в формате chat.history
    """
    try:
        chat = model.start_chat(history=[
            {'role': 'user', 'parts': [FULL_CONTEXT]},
            {'role': 'model', 'parts': ["Здравствуйте! Я готов помочь вам с выбором магистерской программы. Что бы вы хотели узнать?"]},
            *history
        ])
        
        response = chat.send_message(question)
        return response.text
    
    except Exception as e:
        print(f"Ошибка при обращении к Gemini API: {e}")
        return "К сожалению, произошла техническая ошибка. Попробуйте задать вопрос позже."