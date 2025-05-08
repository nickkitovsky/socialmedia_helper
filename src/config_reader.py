from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = ".secret"
        env_file_encoding = "utf-8"


config = Settings()
