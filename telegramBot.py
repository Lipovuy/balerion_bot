from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Функция обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я простой бот, и я работаю!")

# Функция обработки команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй /start, чтобы проверить меня.")

if __name__ == "__main__":
    # Создаем приложение с токеном вашего бота
    TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"  # <- вставь сюда токен от BotFather
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()
