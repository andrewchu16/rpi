from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    debug: bool = False
    allowed_origins: list[str] = ["*"]


config = Config()
