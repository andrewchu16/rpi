"""
Utility functions for the files module.
"""

import os
from typing import Optional, Tuple, Dict, Any
from uuid import UUID
from .constants import CONTENT_PREVIEW_LENGTH


def truncate_content(content: str, max_length: int = CONTENT_PREVIEW_LENGTH) -> str:
    """
    Truncate content to a specified length for preview.
    
    Args:
        content: The content to truncate
        max_length: Maximum length for the preview
        
    Returns:
        str: Truncated content with ellipsis if needed
    """
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def get_file_size(filepath: str) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Optional[int]: File size in bytes, or None if file doesn't exist
    """
    try:
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return None
    except (OSError, IOError):
        return None


def validate_file_type(file_type: str) -> bool:
    """
    Validate if a file type is supported.
    
    Args:
        file_type: The file type to validate
        
    Returns:
        bool: True if the file type is supported, False otherwise
    """
    from .constants import SUPPORTED_FILE_TYPES
    return file_type.lower() in SUPPORTED_FILE_TYPES


def get_table_name_by_type(file_type: str) -> str:
    """
    Get the database table name for a given file type.
    
    Args:
        file_type: The file type (markdown, image, pdf)
        
    Returns:
        str: The corresponding database table name
        
    Raises:
        ValueError: If the file type is not supported
    """
    from .constants import (
        MARKDOWN_DOCUMENTS_TABLE,
        IMAGE_DOCUMENTS_TABLE,
        PDF_DOCUMENTS_TABLE,
        FILE_TYPE_MARKDOWN,
        FILE_TYPE_IMAGE,
        FILE_TYPE_PDF
    )
    
    file_type_lower = file_type.lower()
    
    if file_type_lower == FILE_TYPE_MARKDOWN:
        return MARKDOWN_DOCUMENTS_TABLE
    elif file_type_lower == FILE_TYPE_IMAGE:
        return IMAGE_DOCUMENTS_TABLE
    elif file_type_lower == FILE_TYPE_PDF:
        return PDF_DOCUMENTS_TABLE
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def build_search_query(base_query: str, search_term: Optional[str] = None, file_type: Optional[str] = None) -> Tuple[str, list]:
    """
    Build a SQL search query with optional filters.
    
    Args:
        base_query: The base SQL query
        search_term: Optional search term to filter by title or content
        file_type: Optional file type filter
        
    Returns:
        Tuple[str, list]: The modified query and parameters
    """
    conditions = []
    parameters = []
    
    if search_term:
        conditions.append("(title ILIKE $1 OR content ILIKE $1)")
        parameters.append(f"%{search_term}%")
    
    if file_type:
        # For file type filtering, we'll need to handle this in the service layer
        # since we're querying across multiple tables
        pass
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    return base_query, parameters


def format_file_metadata(file_type: str, content: str, filepath: str) -> Dict[str, Any]:
    """
    Format file metadata based on file type.
    
    Args:
        file_type: The type of file
        content: The file content
        filepath: The file path
        
    Returns:
        Dict[str, Any]: Formatted metadata
    """
    metadata = {
        "file_type": file_type,
        "content_length": len(content),
        "filepath": filepath
    }
    
    # Add type-specific metadata
    if file_type == "image":
        metadata["content_type"] = "image"
    elif file_type == "pdf":
        metadata["content_type"] = "application/pdf"
    elif file_type == "markdown":
        metadata["content_type"] = "text/markdown"
    
    return metadata
