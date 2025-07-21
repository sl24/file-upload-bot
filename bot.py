import os
from pyrogram import Client, filters

# Токен, полученный от BotFather
API_ID = os.getenv("API_ID")  # твой API_ID
API_HASH = os.getenv("API_HASH")  # твой API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN")  # твой токен бота

# Инициализация клиента Pyrogram
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Функция обработки медиа
@app.on_message(filters.media)
async def handle_files(client, message):
    file_size = message.document.file_size if message.document else 0

    # Проверяем размер файла (5MB)
    if file_size > 5 * 1024 * 1024:
        await message.reply("❌ Файл слишком большой. Максимальный размер — 5 МБ.")
        return

    # Скачать файл и отправить ссылку на него (пока просто текст)
    file_path = await message.download()
    await message.reply(f"Файл загружен: {file_path}")

app.run()
