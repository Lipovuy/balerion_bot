import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler, ChatMemberHandler
import requests
import telebot
from telebot import types

key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc0MWFjNjhlLWYxYTItNDZjMi04NWExLTU4MWE2MTcxOGU5MyIsImlhdCI6MTc1ODM5MDk5Niwic3ViIjoiZGV2ZWxvcGVyL2NlMjVkMzc4LTA3ZjUtM2Y2Yi1jNjAxLWQxZjljYTg3Zjc4ZiIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjE3OC4xNTkuMjIxLjExNCJdLCJ0eXBlIjoiY2xpZW50In1dfQ.6ahCyrG6o9aBO_1hnwFrpP1yeU3LQhroxOKwVGMYv7TctnSvGi2DVtLz2Ejj5yEZP1c9bmDKCtGR_JfJ1-2L6A"

url = "https://api.clashofclans.com/v1/clans/%23YUR290VR"

headers = {
    "Accept" : "application/json",
    "authorization" : "Bearer %s" % key
}

response = requests.request("GET", url, headers =headers)

data = response.json()

DATA_FILE = "players.json"

OWNER_ID = 6694139577

# Завантаження даних з JSON
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Збереження даних у JSON
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

players = load_data()

# Перевірка хто додав бота
async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.my_chat_member
    if chat_member is None:
        return

    # Проверяем, что именно бота добавили
    if chat_member.new_chat_member.user.id == context.bot.id:
        adder_id = chat_member.from_user.id

        if adder_id != OWNER_ID:
            # Если добавил кто-то другой → бот сразу выходит
            await context.bot.leave_chat(update.effective_chat.id)

# Обробка повідомлень
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.message.from_user

    # Показати всі ніки
    if text.lower() == "ники":
        if players:
            msg = "Ники в TG | ники в Clash of Clans\n\n"
            for uid, p in players.items():
                # Робимо ім’я клікабельним (веде на профіль у Telegram)
                link = f"[{p['tg_name']}](tg://user?id={uid})"
                msg += f"{link} | {p['coc_nick']}\n"
            await update.message.reply_text(
                msg, parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌Список пустой")
    
    elif text.lower() == "+ник":
        keyboard = []
        row = []
        x = 0
        for index in data["memberList"]:
            x += 1
            row.append(InlineKeyboardButton(f"{index["name"]}", callback_data = f"{index["name"]}"))
            if x % 4 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        for row in keyboard:        # row = список кнопок
            for btn in row[:]:      # row[:] -> копія списку, щоб можна було видаляти
                for _, q in players.items():
                    if q["coc_nick"] == btn.callback_data:
                        row.remove(btn)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выбери свой ник в Clash of Clans⬇",
            reply_markup=reply_markup
        )

# Події які виконуються при натискані на кнопку
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    name = query.data
    user = update.callback_query.from_user
    full_name = user.full_name

    players[str(user.id)] = {
        "tg_name": full_name,
        "coc_nick": name
    }
    save_data(players)
    await query.edit_message_text(text = f"{full_name} выбрал ник {name}")

# Запуск бота
def main():
    app = Application.builder().token("8445533025:AAFPXiVyQyns3K-UeBzI2SjVBLg5f4VI_fw").build()

    app.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()