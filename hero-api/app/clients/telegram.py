import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TelegramError(Exception):
    pass

async def send_message(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise TelegramError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set")
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(api_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        r.raise_for_status()


