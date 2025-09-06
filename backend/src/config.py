from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    debug: bool = False
    allowed_origins: list[str] = ["*"]
    
    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatdb"
    database_echo: bool = False

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Split by comma and strip whitespace, filter out empty strings
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    


config = Settings()

