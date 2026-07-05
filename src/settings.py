import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    PDF_PASSWORD = os.getenv(
        "PDF_PASSWORD"
    )

    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    TELEGRAM_CHAT_ID = os.getenv(
        "TELEGRAM_CHAT_ID"
    )


settings = Settings()