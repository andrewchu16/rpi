from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class BaseDocument(BaseModel):
    """Base model for document tables with common fields."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    filepath: str = Field(..., description="File path where the document is stored")
    content: str = Field(..., description="Content of the document (OCR text for images, stripped markdown for documents)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the document was created")


class ImageDocument(BaseDocument):
    """Model for image documents with OCR content."""
    content: str = Field(..., description="OCR extracted text content from the image")


class MarkdownDocument(BaseDocument):
    """Model for markdown documents with stripped metadata."""
    content: str = Field(..., description="Markdown content with metadata stripped out")
