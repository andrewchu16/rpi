"""
Constants for the files module.
"""

# File types
FILE_TYPE_MARKDOWN = "markdown"
FILE_TYPE_IMAGE = "image"
FILE_TYPE_PDF = "pdf"

# Supported file types
SUPPORTED_FILE_TYPES = [FILE_TYPE_MARKDOWN, FILE_TYPE_IMAGE, FILE_TYPE_PDF]

# Default pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Content preview length
CONTENT_PREVIEW_LENGTH = 200

# Database table names
MARKDOWN_DOCUMENTS_TABLE = "markdown_documents"
IMAGE_DOCUMENTS_TABLE = "image_documents"
PDF_DOCUMENTS_TABLE = "pdf_documents"
