from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    allowed_origins: list[str] = ["*"]
    
    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatdb"
    database_echo: bool = False
    


config = Settings()

