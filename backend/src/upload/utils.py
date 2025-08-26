import os
from fastapi import UploadFile
from PIL import Image
import io
from typing import Tuple
import PyPDF2
from .config import upload_settings
from .constants import MARKDOWN_UPLOAD_SUBDIR, IMAGE_UPLOAD_SUBDIR, PDF_UPLOAD_SUBDIR
from .exceptions import (
    FileTooLargeError,
    InvalidMarkdownTypeError,
    InvalidImageTypeError,
    InvalidPDFTypeError,
    InvalidUTF8Error
)


def check_file_size(file: UploadFile, max_size: int) -> int:
    """
    Check if the file size is within the allowed limit.
    
    Args:
        file: The uploaded file
        max_size: Maximum allowed file size in bytes
        
    Returns:
        int: The actual file size in bytes
        
    Raises:
        FileTooLargeError: If the file exceeds the maximum size
    """
    file.file.seek(0, 2)  # Seek to the end of the file
    file_size = file.file.tell()  # Get current position (file size)
    file.file.seek(0)  # Reset file pointer to the beginning

    if file_size > max_size:
        max_size_mb = max_size / 1024 / 1024
        raise FileTooLargeError(max_size_mb=max_size_mb)

    return file_size


def validate_markdown_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a valid markdown/text file.
    
    Args:
        file: The uploaded file
        
    Raises:
        InvalidMarkdownTypeError: If the file is not a valid markdown/text file
        InvalidUTF8Error: If the file contains invalid UTF-8 content
    """
    content_type = file.content_type or ""
    
    # Check content type
    if not any(allowed_type in content_type.lower() for allowed_type in upload_settings.allowed_markdown_types):
        raise InvalidMarkdownTypeError()

    # Read content to verify it's plaintext
    content = file.file.read()
    try:
        _ = content.decode("utf-8")
    except UnicodeDecodeError:
        raise InvalidUTF8Error()
    finally:
        file.file.seek(0)  # Reset pointer for service to re-read


def validate_image_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a valid image.
    
    Args:
        file: The uploaded file
        
    Raises:
        InvalidImageTypeError: If the file is not a valid image
    """
    content_type = file.content_type or ""
    
    if not content_type.startswith("image/"):
        raise InvalidImageTypeError()


def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a valid PDF.
    
    Args:
        file: The uploaded file
        
    Raises:
        InvalidPDFTypeError: If the file is not a valid PDF
    """
    content_type = file.content_type or ""
    
    if content_type not in upload_settings.allowed_pdf_types:
        raise InvalidPDFTypeError()


def save_file_to_disk(content: bytes, filename: str, subdir: str) -> str:
    """
    Save file content to disk in the specified subdirectory.
    
    Args:
        content: File content as bytes
        filename: Name to save the file as
        subdir: Subdirectory within the upload directory
        
    Returns:
        str: Full filepath where the file was saved
    """
    upload_subdir = os.path.join(upload_settings.upload_dir, subdir)
    os.makedirs(upload_subdir, exist_ok=True)
    
    filepath = os.path.join(upload_subdir, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    return filepath


def get_image_metadata(content: bytes) -> Tuple[int, int, str, str]:
    """
    Extract metadata from image content.
    
    Args:
        content: Image content as bytes
        
    Returns:
        Tuple[int, int, str, str]: (width, height, format, mode)
    """
    image = Image.open(io.BytesIO(content))
    width, height = image.size
    img_format = image.format
    mode = image.mode
    
    return width, height, img_format, mode


def get_pdf_metadata(content: bytes) -> Tuple[int, str]:
    """
    Extract metadata from PDF content.
    
    Args:
        content: PDF content as bytes
        
    Returns:
        Tuple[int, str]: (page_count, extracted_text)
    """
    pdf_file = io.BytesIO(content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    page_count = len(pdf_reader.pages)
    extracted_text = ""
    
    # Extract text from all pages
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text += page_text + "\n"
    
    return page_count, extracted_text.strip()
