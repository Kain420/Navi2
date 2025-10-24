import os
import logging
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация из переменных окружения
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_string = os.getenv('SESSION_STRING')
source_channel = int(os.getenv('SOURCE_CHANNEL'))
destination_channel = int(os.getenv('DESTINATION_CHANNEL'))

# Инициализация клиента Telegram
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash
)

@app.route('/')
def index():
    return "Bot is running!"

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        # Пересылаем сообщение
        await client.forward_messages(
            entity=destination_channel,
            messages=event.message
        )
        logger.info(f"Переслано сообщение: {event.message.id}")
    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def start_telethon():
    await client.start()
    logger.info("Telethon client started")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    from threading import Thread

    # Запускаем Telethon в отдельном потоке
    def run_telethon():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_telethon())

    thread = Thread(target=run_telethon, daemon=True)
    thread.start()

    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=5000)
