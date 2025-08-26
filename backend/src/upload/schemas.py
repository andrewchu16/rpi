from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class BaseUploadResponse(BaseModel):
    """Base model for upload responses with common fields."""
    filename: str = Field(..., description="Original filename of the uploaded file")
    size: int = Field(..., description="Size of the uploaded file in bytes")
    content_type: str = Field(..., description="MIME type of the uploaded file")
    document_id: UUID = Field(..., description="Unique identifier of the created document")
    filepath: str = Field(..., description="Path where the file was saved")


class MarkdownUploadResponse(BaseUploadResponse):
    """Response model for markdown file uploads."""
    text_length: int = Field(..., description="Length of the text content in characters")


class ImageUploadResponse(BaseUploadResponse):
    """Response model for image file uploads."""
    width: int = Field(..., description="Width of the image in pixels")
    height: int = Field(..., description="Height of the image in pixels")
    format: Optional[str] = Field(None, description="Image format (JPEG, PNG, etc.)")
    mode: str = Field(..., description="Image color mode (RGB, RGBA, etc.)")


class UploadSuccessResponse(BaseModel):
    """Wrapper response for successful uploads."""
    message: str = Field(..., description="Success message")
    file_info: BaseUploadResponse = Field(..., description="File upload information")
