from fastapi import APIRouter, Depends, File, UploadFile
from ..auth.dependencies import get_current_user
from ..auth.schemas import Token
from .schemas import UploadSuccessResponse
from .service import UploadService
from .utils import (
    check_file_size,
    validate_markdown_file,
    validate_image_file
)
from .config import upload_settings
from .constants import MARKDOWN_UPLOAD_SUCCESS, IMAGE_UPLOAD_SUCCESS

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
    result = await UploadService.process_markdown(file, file_size)
    
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
    result = await UploadService.process_image(file, file_size)
    
    return UploadSuccessResponse(
        message=IMAGE_UPLOAD_SUCCESS,
        file_info=result
    )
