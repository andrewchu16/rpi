from fastapi import HTTPException, status
from .constants import (
    FILE_TOO_LARGE_MESSAGE,
    INVALID_MARKDOWN_TYPE_MESSAGE,
    INVALID_IMAGE_TYPE_MESSAGE,
    INVALID_UTF8_MESSAGE
)


class UploadError(HTTPException):
    """Base upload error"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class FileTooLargeError(UploadError):
    """Raised when the uploaded file exceeds the maximum allowed size"""
    def __init__(self, max_size_mb: float):
        detail = FILE_TOO_LARGE_MESSAGE.format(max_size_mb=max_size_mb)
        super().__init__(detail=detail, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class InvalidMarkdownTypeError(UploadError):
    """Raised when the uploaded file is not a valid markdown/text file"""
    def __init__(self):
        super().__init__(detail=INVALID_MARKDOWN_TYPE_MESSAGE, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class InvalidImageTypeError(UploadError):
    """Raised when the uploaded file is not a valid image"""
    def __init__(self):
        super().__init__(detail=INVALID_IMAGE_TYPE_MESSAGE, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class InvalidUTF8Error(UploadError):
    """Raised when the uploaded file contains invalid UTF-8 content"""
    def __init__(self):
        super().__init__(detail=INVALID_UTF8_MESSAGE, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
