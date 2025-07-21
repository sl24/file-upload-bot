import os
from pyrogram import Client

# Загружаем переменные окружения
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Хэндлер на команду /start
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Я твой Телеграм-бот.")

if __name__ == "__main__":
    app.run()
