import os
from pyrogram import Client, filters

# Загружаем переменные окружения
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Максимальный размер файла: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # в байтах

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Я твой Телеграм-бот.\nОтправь мне файл до 5MB (кроме .py и .exe).")

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message):
    # Определяем объект файла
    file = message.document or message.video or message.audio or message.photo

    if not file:
        await message.reply("Не удалось получить файл.")
        return

    # Проверка размера файла
    if file.file_size > MAX_FILE_SIZE:
        await message.reply("❌ Ошибка: размер файла превышает 5MB.")
        return

    # Проверка расширения, если это документ
    if message.document:
        filename = message.document.file_name.lower()
        if filename.endswith(('.py', '.exe')):
            await message.reply("❌ Ошибка: файлы с расширением .py и .exe не принимаются.")
            return

    await message.reply("✅ Файл принят. Скоро получите ссылку на скачивание.")  # тут позже добавим логику загрузки

if __name__ == "__main__":
    app.run()
