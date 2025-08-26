from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings): 
    """Application settings using Pydantic BaseSettings for type safety and validation."""
    
    # Global configuration
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Database Configuration
    database_host: str = Field(default="db", description="Database host")
    database_port: int = Field(default=5432, description="Database port")
    database_user: str = Field(default="postgres", description="Database username")
    database_password: str = Field(default="postgres", description="Database password")
    database_name: str = Field(default="rpi_db", description="Database name")
    

# Create a global settings instance
settings = Settings()
