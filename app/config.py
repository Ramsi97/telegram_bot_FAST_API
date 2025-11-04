from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Telegram Bot Settings
    BOT_TOKEN: str
    WEBHOOK_URL: str
    API_BASE_URL: str = "https://api.telegram.org"
    BOT_NAME: str = "PDF Image Bot"
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "storage" / "outputs"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)