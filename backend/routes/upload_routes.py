from fastapi import APIRouter, Depends, File, UploadFile

from security.token import verify_access_token
from controllers import UploadController
from models.uploads import MarkdownUploadResponse, ImageUploadResponse, UploadSuccessResponse

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/md", response_model=UploadSuccessResponse)
async def upload_markdown(
    file: UploadFile = File(..., description="Markdown file"),
    _: bool = Depends(verify_access_token)
) -> UploadSuccessResponse:
    """
    Upload a markdown file (max 4MB)
    
    This endpoint validates:
    - File size (must be under 4MB)
    - Content type (must be text/markdown or similar)
    - Content must be valid UTF-8 text
    """
    result = await UploadController.upload_markdown(file)
    return UploadSuccessResponse(
        message="Markdown file uploaded successfully",
        file_info=result
    )

@router.post("/image", response_model=UploadSuccessResponse)
async def upload_image(
    file: UploadFile = File(..., description="Image file"),
    _: bool = Depends(verify_access_token)
) -> UploadSuccessResponse:
    """
    Upload an image file (max 4MB)
    
    This endpoint validates:
    - File size (must be under 4MB)
    - Content type (must be an image format)
    - File must be a valid image
    
    The image is processed using Pillow and basic metadata is returned
    """
    result = await UploadController.upload_image(file)
    
    return UploadSuccessResponse(
        message="Image uploaded successfully",
        file_info=result
    )