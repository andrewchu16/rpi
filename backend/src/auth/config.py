from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """Authentication settings using Pydantic BaseSettings for type safety and validation."""
    
    # Security configuration
    secret_key: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7,  # 1 week
        description="Access token expiration time in minutes"
    )
    
    # API access code
    access_code: str = Field(
        default="your-secure-access-code",
        description="Password that protects the API"
    )


# Create a global auth settings instance
auth_settings = AuthSettings()
