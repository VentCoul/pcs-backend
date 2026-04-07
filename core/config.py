import os
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.poster_account = os.getenv("POSTER_ACCOUNT")
        self.poster_token = os.getenv("POSTER_TOKEN")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.db_url = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'pcs.db')}"

settings = Settings()
