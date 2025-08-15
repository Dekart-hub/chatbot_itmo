import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from llm_core import get_gemini_response

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение."""
    context.user_data['history'] = []
    await update.message.reply_text(
        "Здравствуйте! Я бот-помощник по магистерским программам ИТМО 'Искусственный интеллект' и 'Управление AI-продуктами'.\n\n"
        "Задайте мне любой вопрос о них, например:\n"
        "• Чем отличаются эти две программы?\n"
        "• Какие дисциплины я буду изучать на первом курсе AI Product?\n"
        "• Расскажи о научных руководителях."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справку."""
    await update.message.reply_text("Просто напишите ваш вопрос, и я постараюсь на него ответить, основываясь на официальной информации с сайта ИТМО. Чтобы начать диалог заново, используйте команду /start.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения от пользователя."""
    user_question = update.message.text
    
    if 'history' not in context.user_data:
        context.user_data['history'] = []
        
    history = context.user_data['history']

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    answer = get_gemini_response(user_question, history)
    
    history.append({'role': 'user', 'parts': [user_question]})
    history.append({'role': 'model', 'parts': [answer]})
    # Ограничиваем историю, чтобы не превышать лимиты
    context.user_data['history'] = history[-10:] 

    await update.message.reply_text(answer)

def main() -> None:
    """Основная функция для запуска бота."""
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Не найден TELEGRAM_BOT_TOKEN в .env файле!")
        return
        
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()