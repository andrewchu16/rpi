from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID


class FileListItem(BaseModel):
    """Schema for a single file in a list response."""
    id: UUID = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    filepath: str = Field(..., description="File path where the document is stored")
    content_preview: str = Field(..., description="Preview of the document content (first 200 characters)")
    created_at: datetime = Field(..., description="Timestamp when the document was created")
    file_type: str = Field(..., description="Type of document (markdown, image, pdf)")


class FileListResponse(BaseModel):
    """Schema for paginated file list response."""
    files: List[FileListItem] = Field(..., description="List of files")
    total_count: int = Field(..., description="Total number of files")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class FileDetailResponse(BaseModel):
    """Schema for detailed file information."""
    id: UUID = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    filepath: str = Field(..., description="File path where the document is stored")
    content: str = Field(..., description="Full content of the document")
    created_at: datetime = Field(..., description="Timestamp when the document was created")
    file_type: str = Field(..., description="Type of document (markdown, image, pdf)")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    metadata: Optional[dict] = Field(None, description="Additional metadata for the file")


class FileSearchRequest(BaseModel):
    """Schema for file search request."""
    query: Optional[str] = Field(None, description="Search query to filter files by title or content")
    file_type: Optional[str] = Field(None, description="Filter by file type (markdown, image, pdf)")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")


class FileDeleteResponse(BaseModel):
    """Schema for file deletion response."""
    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Response message")
    deleted_file_id: Optional[UUID] = Field(None, description="ID of the deleted file")
