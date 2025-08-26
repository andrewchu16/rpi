"""
Router for the files module.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from .service import files_service
from .schemas import (
    FileListResponse,
    FileDetailResponse,
    FileSearchRequest,
    FileDeleteResponse
)
from .exceptions import (
    FileNotFoundError,
    InvalidFileTypeError,
    FileAccessError,
    FileDeletionError
)
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, SUPPORTED_FILE_TYPES

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Number of items per page"),
    file_type: Optional[str] = Query(default=None, description="Filter by file type (markdown, image, pdf)"),
    search: Optional[str] = Query(default=None, description="Search query for title or content")
) -> FileListResponse:
    """
    List uploaded files with pagination and optional filtering.
    
    Args:
        page: Page number for pagination
        page_size: Number of items per page (max 100)
        file_type: Optional filter by file type
        search: Optional search query for title or content
        
    Returns:
        FileListResponse: Paginated list of files
        
    Raises:
        HTTPException: If file_type is invalid
    """
    try:
        return await files_service.list_files(
            page=page,
            page_size=page_size,
            file_type=file_type,
            search_query=search
        )
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileAccessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{file_id}", response_model=FileDetailResponse)
async def get_file_detail(
    file_id: UUID = Path(..., description="The ID of the file to retrieve"),
    file_type: Optional[str] = Query(default=None, description="File type hint for faster lookup (markdown, image, pdf)")
) -> FileDetailResponse:
    """
    Get detailed information about a specific file.
    
    Args:
        file_id: The ID of the file to retrieve
        file_type: Optional file type hint for faster lookup
        
    Returns:
        FileDetailResponse: Detailed file information
        
    Raises:
        HTTPException: If file is not found or file_type is invalid
    """
    try:
        return await files_service.get_file_detail(file_id, file_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileAccessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/search", response_model=FileListResponse)
async def search_files(search_request: FileSearchRequest) -> FileListResponse:
    """
    Search files with advanced filtering.
    
    Args:
        search_request: Search parameters including query, file_type, and pagination
        
    Returns:
        FileListResponse: Search results with pagination
        
    Raises:
        HTTPException: If search parameters are invalid
    """
    try:
        return await files_service.search_files(search_request)
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileAccessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: UUID = Path(..., description="The ID of the file to delete"),
    file_type: Optional[str] = Query(default=None, description="File type hint for faster lookup (markdown, image, pdf)")
) -> FileDeleteResponse:
    """
    Delete a file from the database and filesystem.
    
    Args:
        file_id: The ID of the file to delete
        file_type: Optional file type hint for faster lookup
        
    Returns:
        FileDeleteResponse: Deletion result
        
    Raises:
        HTTPException: If file is not found, file_type is invalid, or deletion fails
    """
    try:
        return await files_service.delete_file(file_id, file_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileDeletionError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/types/supported")
async def get_supported_file_types() -> dict:
    """
    Get list of supported file types.
    
    Returns:
        dict: List of supported file types
    """
    return {
        "supported_types": SUPPORTED_FILE_TYPES,
        "description": "List of supported file types for viewing and management"
    }
