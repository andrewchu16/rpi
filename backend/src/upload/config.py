from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class UploadSettings(BaseSettings):
    """Upload settings using Pydantic BaseSettings for type safety and validation."""
    
    # Upload configuration
    upload_dir: str = Field(default="uploads/", description="Directory for file uploads")
    max_file_size: int = Field(
        default=4 * 1024 * 1024,  # 4MB default
        description="Maximum file size in bytes"
    )
    
    # File type configurations
    allowed_markdown_types: List[str] = Field(
        default=[
            "text/markdown",
            "text/plain",
            "text/x-markdown",
            "application/markdown"
        ],
        description="Allowed MIME types for markdown files"
    )
    
    allowed_image_types: List[str] = Field(
        default=[
            "image/jpeg",
            "image/jpg", 
            "image/png",
            "image/gif",
            "image/bmp",
            "image/webp"
        ],
        description="Allowed MIME types for image files"
    )


# Create a global upload settings instance
upload_settings = UploadSettings()
