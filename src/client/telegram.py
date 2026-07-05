import httpx

from src.settings import settings


class TelegramClient:

    def __init__(self):

        self.bot_token = (
            settings.TELEGRAM_BOT_TOKEN
        )

        self.chat_id = (
            settings.TELEGRAM_CHAT_ID
        )


    async def send_message(
        self,
        message: str
    ):

        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is missing"
            )

        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID is missing"
            )


        telegram_url = (

            f"https://api.telegram.org/"

            f"bot{self.bot_token}/"

            f"sendMessage"

        )


        payload = {

            "chat_id":
                self.chat_id,

            "text":
                message

        }


        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                telegram_url,
                json=payload
            )


        response.raise_for_status()


        return response.json()