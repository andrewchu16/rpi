"""
Custom exceptions for the files module.
"""

from fastapi import HTTPException, status


class FileNotFoundError(HTTPException):
    """Raised when a file is not found."""
    def __init__(self, file_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found"
        )


class InvalidFileTypeError(HTTPException):
    """Raised when an invalid file type is specified."""
    def __init__(self, file_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file_type}. Supported types: markdown, image, pdf"
        )


class FileAccessError(HTTPException):
    """Raised when there's an error accessing a file."""
    def __init__(self, file_id: str, error: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing file {file_id}: {error}"
        )


class FileDeletionError(HTTPException):
    """Raised when there's an error deleting a file."""
    def __init__(self, file_id: str, error: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file {file_id}: {error}"
        )
