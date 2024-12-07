import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoModelForCausalLM, AutoTokenizer

# Настройка API ключей
TELEGRAM_API_KEY = "7662575975:AAH8canl9W3qizAk50oZ8Q48AEB8fsLQ7JQ"
HUGGINGFACE_API_KEY = "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"
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

# Настройка модели
print("Загрузка модели, подожди немного...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HUGGINGFACE_API_KEY)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, token=HUGGINGFACE_API_KEY)
print("Модель загружена!")

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Глобальный словарь для хранения языковых настроек пользователей
user_languages = {}

# Приветственное сообщение
WELCOME_MESSAGE = {
    "en": (
        "Hi! 👋 I'm your personal assistant powered by Llama 2.\n"
        "I can:\n"
        "- Answer questions\n"
        "- Assist with tasks\n"
        "- Chat in English or Russian\n"
        "\nType your question or choose your language using the /language command."
    ),
    "ru": (
        "Привет! 👋 Я твой персональный помощник на базе Llama 2.\n"
        "Я могу:\n"
        "- Отвечать на вопросы\n"
        "- Помогать с задачами\n"
        "- Общаться на русском или английском\n"
        "\nНапиши свой вопрос или выбери язык с помощью команды /language."
    ),
}

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_languages[user_id] = "ru"  # По умолчанию русский язык
    language = user_languages[user_id]
    await update.message.reply_text(WELCOME_MESSAGE[language])

# Обработка команды /language
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["English", "Русский"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Choose your language / Выберите язык:", reply_markup=reply_markup)

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    language = user_languages.get(user_id, "ru")

    user_input = update.message.text
    if user_input.lower() in ["english", "русский"]:
        if user_input.lower() == "english":
            user_languages[user_id] = "en"
            await update.message.reply_text("Language changed to English. 👌")
        else:
            user_languages[user_id] = "ru"
            await update.message.reply_text("Язык изменён на русский. 👌")
        return

    # Генерация ответа модели
    inputs = tokenizer.encode(user_input, return_tensors="pt")
    outputs = model.generate(inputs, max_length=1000, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    await update.message.reply_text(response)

# Основной блок
if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("language", language))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен. Нажми Ctrl+C для остановки.")
    application.run_polling()
