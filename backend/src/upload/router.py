from fastapi import APIRouter, Depends, File, UploadFile
from typing import List
from ..auth.dependencies import get_current_user
from ..auth.schemas import Token
from .schemas import UploadSuccessResponse, BulkUploadResponse
from .service import upload_service
from .utils import (
    check_file_size,
    validate_markdown_file,
    validate_image_file,
    validate_pdf_file
)
from .config import upload_settings
from .constants import MARKDOWN_UPLOAD_SUCCESS, IMAGE_UPLOAD_SUCCESS, PDF_UPLOAD_SUCCESS

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/md", response_model=UploadSuccessResponse)
async def upload_markdown(
    file: UploadFile = File(..., description="Markdown file"),
    _: Token = Depends(get_current_user)
) -> UploadSuccessResponse:
    """
    Upload a markdown file (max 4MB)
    
    This endpoint validates:
    - File size (must be under 4MB)
    - Content type (must be text/markdown or similar)
    - Content must be valid UTF-8 text
    """
    # Check file size
    file_size = check_file_size(file, upload_settings.max_file_size)
    
    # Validate file type and content
    validate_markdown_file(file)
    
    # Process the file
    result = await upload_service.process_markdown(file, file_size)
    
    return UploadSuccessResponse(
        message=MARKDOWN_UPLOAD_SUCCESS,
        file_info=result
    )


@router.post("/image", response_model=UploadSuccessResponse)
async def upload_image(
    file: UploadFile = File(..., description="Image file"),
    _: Token = Depends(get_current_user)
) -> UploadSuccessResponse:
    """
    Upload an image file (max 4MB)
    
    This endpoint validates:
    - File size (must be under 4MB)
    - Content type (must be an image format)
    - File must be a valid image
    
    The image is processed using Pillow and basic metadata is returned
    """
    # Check file size
    file_size = check_file_size(file, upload_settings.max_file_size)
    
    # Validate file type
    validate_image_file(file)
    
    # Process the file
    result = await upload_service.process_image(file, file_size)
    
    return UploadSuccessResponse(
        message=IMAGE_UPLOAD_SUCCESS,
        file_info=result
    )


@router.post("/pdf", response_model=UploadSuccessResponse)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file"),
    _: Token = Depends(get_current_user)
) -> UploadSuccessResponse:
    """
    Upload a PDF file (max 4MB)
    
    This endpoint validates:
    - File size (must be under 4MB)
    - Content type (must be application/pdf)
    - File must be a valid PDF
    
    The PDF is processed using PyPDF2 and text content is extracted
    """
    # Check file size
    file_size = check_file_size(file, upload_settings.max_file_size)
    
    # Validate file type
    validate_pdf_file(file)
    
    # Process the file
    result = await upload_service.process_pdf(file, file_size)
    
    return UploadSuccessResponse(
        message=PDF_UPLOAD_SUCCESS,
        file_info=result
    )


@router.post("/bulk", response_model=BulkUploadResponse)
async def bulk_upload(
    files: List[UploadFile] = File(..., description="Multiple files (markdown, images, or PDFs)"),
    _: Token = Depends(get_current_user)
) -> BulkUploadResponse:
    """
    Upload multiple files of different types in a single request (max 4MB per file)
    
    This endpoint accepts:
    - Markdown files (text/markdown, text/plain, etc.)
    - Image files (image/jpeg, image/png, etc.)
    - PDF files (application/pdf)
    
    Each file is processed according to its type and the results are returned
    """
    # Process all files
    result = await upload_service.process_bulk_upload(files)
    
    return result
