"""
Files module for viewing and managing uploaded documents.
"""

from .router import router
from .service import files_service

__all__ = ["router", "files_service"]
