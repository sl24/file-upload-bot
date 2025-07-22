import os
import asyncio
import hashlib
import time
import zipfile
from urllib.parse import quote

from pyrogram import Client, filters
from pyrogram.types import Message
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn

from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=1)
fastapi_app = FastAPI()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

media_groups = {}

def generate_hash(text: str) -> str:
    return hashlib.md5(f"{text}_{time.time()}".encode()).hexdigest()[:8]

def get_file_size(message: Message):
    if message.document:
        return message.document.file_size
    elif message.video:
        return message.video.file_size
    elif message.animation:
        return message.animation.file_size
    elif message.photo:
        return message.photo.file_size
    return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Отправь файл (до 5MB) или несколько файлов одной группой — создам архив с ссылкой.")

@app.on_message(filters.media)
async def handle_files(client: Client, message: Message):
    media_group_id = message.media_group_id
    if media_group_id:
        if media_group_id not in media_groups:
            media_groups[media_group_id] = {"messages": [], "timer": None}
        media_groups[media_group_id]["messages"].append(message)

        timer = media_groups[media_group_id]["timer"]
        if timer:
            timer.cancel()
        media_groups[media_group_id]["timer"] = asyncio.create_task(delayed_process(media_group_id))
    else:
        await handle_single_file(client, message)

async def handle_single_file(client: Client, message: Message):
    size = get_file_size(message)
    if size and size > MAX_FILE_SIZE:
        await message.reply("❌ Файл слишком большой. Максимум 5 МБ.")
        return

    if message.document:
        name, ext = os.path.splitext(message.document.file_name)
        if ext.lower() in ['.py', '.exe']:
            await message.reply("❌ Файл .py и .exe запрещены.")
            return
        file_name = f"{name}_{generate_hash(message.document.file_unique_id)}{ext}"
    elif message.video:
        file_name = f"{message.video.file_unique_id}_{generate_hash(message.video.file_unique_id)}.mp4"
    elif message.animation:
        file_name = f"{message.animation.file_unique_id}_{generate_hash(message.animation.file_unique_id)}.gif"
    elif message.photo:
        file_name = f"{message.photo.file_unique_id}_{generate_hash(message.photo.file_unique_id)}.jpg"
    else:
        file_name = f"{generate_hash(str(time.time()))}.dat"

    file_path = os.path.join(UPLOAD_DIR, file_name)
    await message.download(file_name=file_path)

    link = f"https://file-upload-bot.onrender.com/download/{quote(file_name)}"
    await message.reply(f"✅ Ваша ссылка на скачивание:\n{link}")

async def delayed_process(media_group_id):
    await asyncio.sleep(3)
    await process_media_group(media_group_id)

async def process_media_group(media_group_id):
    data = media_groups.pop(media_group_id, None)
    if not data:
        return

    messages = data["messages"]
    for m in messages:
        size = get_file_size(m)
        if size and size > MAX_FILE_SIZE:
            await messages[0].reply("❌ Один из файлов слишком большой (>5 МБ), архив не создан.")
            return

    temp_files = []
    for m in messages:
        filename = None
        if m.document:
            name, ext = os.path.splitext(m.document.file_name)
            filename = f"{name}_{generate_hash(m.document.file_unique_id)}{ext}"
        elif m.video:
            filename = f"{m.video.file_unique_id}_{generate_hash(m.video.file_unique_id)}.mp4"
        elif m.animation:
            filename = f"{m.animation.file_unique_id}_{generate_hash(m.animation.file_unique_id)}.gif"
        elif m.photo:
            filename = f"{m.photo.file_unique_id}_{generate_hash(m.photo.file_unique_id)}.jpg"
        if filename:
            file_path = os.path.join(UPLOAD_DIR, filename)
            await m.download(file_name=file_path)
            temp_files.append((file_path, filename))

    archive_name = f"archive_{media_group_id}_{generate_hash(str(time.time()))}.zip"
    archive_path = os.path.join(UPLOAD_DIR, archive_name)
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        for file_path, filename in temp_files:
            zipf.write(file_path, arcname=filename)

    link = f"https://file-upload-bot.onrender.com/download/{quote(archive_name)}"
    await messages[0].reply(f"✅ Архив готов: {link}")

@fastapi_app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, filename=filename, media_type="application/octet-stream")


async def run_bot():
    await app.start()
    await app.idle()

def start_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=10000, log_level="info")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    print("Бот запущен. Запускаем FastAPI...")
    start_fastapi()
