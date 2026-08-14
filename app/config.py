import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("BASE_URL_DB")
    app_host: str = 'localhost'
    app_port: int = 5432

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()