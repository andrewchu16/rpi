from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=10, ge=1, le=100, description="Number of items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


def calculate_pagination(total: int, page: int, size: int) -> dict:
    """
    Calculate pagination metadata.
    
    Args:
        total: Total number of items
        page: Current page number
        size: Number of items per page
        
    Returns:
        dict: Pagination metadata
    """
    pages = (total + size - 1) // size  # Ceiling division
    has_next = page < pages
    has_prev = page > 1
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": has_next,
        "has_prev": has_prev
    }


def get_offset(page: int, size: int) -> int:
    """
    Calculate the offset for SQL queries.
    
    Args:
        page: Page number (1-based)
        size: Number of items per page
        
    Returns:
        int: Offset for SQL LIMIT/OFFSET
    """
    return (page - 1) * size
