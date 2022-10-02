import pathlib

from pydantic import BaseSettings


class Settings(BaseSettings):
    STOCK_API_KEY: str
    NEWS_API_KEY: str
    BOT_TOKEN: str
    CHAT_ID: str

    class Config:
        env_file = pathlib.Path(__file__).parent.parent / ".env"
        env_file_encoding = 'utf-8'


ENV_VARS = Settings()
