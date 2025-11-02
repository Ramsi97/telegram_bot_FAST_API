from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_URL: str
    API_BASE_URL: str = "https://api.telegram.org"
    BOT_NAME: str = "PDF Image Bot"

    class Config:
        env_file = ".env"

settings = Settings()
