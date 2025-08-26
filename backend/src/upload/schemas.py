from pydantic import BaseModel, Field
from typing import Optional, List, Union
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


class PDFUploadResponse(BaseUploadResponse):
    """Response model for PDF file uploads."""
    page_count: int = Field(..., description="Number of pages in the PDF")
    text_length: int = Field(..., description="Length of the extracted text content in characters")


class UploadSuccessResponse(BaseModel):
    """Wrapper response for successful uploads."""
    message: str = Field(..., description="Success message")
    file_info: BaseUploadResponse = Field(..., description="File upload information")


class BulkUploadItem(BaseModel):
    """Individual file upload result in bulk upload."""
    filename: str = Field(..., description="Original filename of the uploaded file")
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Success or error message")
    file_info: Optional[Union[MarkdownUploadResponse, ImageUploadResponse, PDFUploadResponse]] = Field(
        None, description="File upload information (if successful)"
    )


class BulkUploadResponse(BaseModel):
    """Response model for bulk file uploads."""
    total_files: int = Field(..., description="Total number of files processed")
    successful_uploads: int = Field(..., description="Number of successfully uploaded files")
    failed_uploads: int = Field(..., description="Number of failed uploads")
    results: List[BulkUploadItem] = Field(..., description="Results for each uploaded file")
