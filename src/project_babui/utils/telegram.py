import os

import httpx


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        self.start_client()

    def send_message(self, msg: str):
        payload = {
            "chat_id": self.chat_id,
            "text": msg,
            "parse_mode": "HTML",  # Allows for bolding/links
        }
        response = self.sync_client.post(self.api_url, data=payload)
        response.raise_for_status()

    def start_client(self):
        self.sync_client = httpx.Client(http2=True)

    def close_client(self):
        self.sync_client.close()


class TelegramBotAsync:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        self.start_client()

    async def send_message(self, msg: str):
        payload = {
            "chat_id": self.chat_id,
            "text": msg,
            "parse_mode": "HTML",  # Allows for bolding/links
        }

        response = await self.async_client.post(self.api_url, data=payload)
        response.raise_for_status()

    def start_client(self):
        self.async_client = httpx.AsyncClient(http2=True)

    async def close_client(self):
        await self.async_client.aclose()
