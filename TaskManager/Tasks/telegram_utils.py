
# Utility functions for sending Telegram messages from Django

from django.conf import settings
from telegram import Bot, error as tg_error

def send_telegram_message(chat_id, message):
    """
    Sends a message to a Telegram user or group using the bot token from Django settings.
    Handles errors and logs output for debugging.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    print(f"[Telegram] Using token: {token}")
    print(f"[Telegram] Sending message to chat_id={chat_id}: {message}")
    if not token:
        print("[Telegram] Error: TELEGRAM_BOT_TOKEN is not set in Django settings.")
        return False
    import asyncio
    try:
        bot = Bot(token=token)
        # Run the coroutine in the event loop
        asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        print("[Telegram] Message sent successfully.")
        return True
    except tg_error.TelegramError as e:
        print(f"[Telegram] Telegram API error: {e}")
    except Exception as e:
        print(f"[Telegram] Unexpected error: {e}")
    return False

# Usage example:
# from .telegram_utils import send_telegram_message
# send_telegram_message(chat_id='123456789', message='Hello from Django!')
