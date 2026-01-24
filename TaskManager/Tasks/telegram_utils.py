import os
import asyncio
from django.conf import settings
from telegram import Bot

async def async_send_telegram_message(chat_id, message):
    """
    Sends a message to a Telegram user or group using the bot (asyncio).
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        raise ValueError("Telegram bot token not set in settings.")
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

def send_telegram_message(chat_id, message):
    """
    Synchronous wrapper for async_send_telegram_message for use in Django signals/views.
    """
    try:
        asyncio.run(async_send_telegram_message(chat_id, message))
    except RuntimeError:
        # If already in an event loop (e.g., in some async context), use create_task
        loop = asyncio.get_event_loop()
        loop.create_task(async_send_telegram_message(chat_id, message))
