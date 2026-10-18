from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()
from typing import Optional
class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: Optional[str] = None
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")


settings = Settings()