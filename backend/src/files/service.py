"""
Service layer for the files module.
"""

import os
from typing import List, Optional, Tuple
from uuid import UUID
from ..database import get_db_pool
from .schemas import (
    FileListItem,
    FileListResponse,
    FileDetailResponse,
    FileSearchRequest,
    FileDeleteResponse
)
from .constants import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    FILE_TYPE_MARKDOWN,
    FILE_TYPE_IMAGE,
    FILE_TYPE_PDF,
    MARKDOWN_DOCUMENTS_TABLE,
    IMAGE_DOCUMENTS_TABLE,
    PDF_DOCUMENTS_TABLE
)
from .exceptions import (
    FileNotFoundError,
    InvalidFileTypeError,
    FileAccessError,
    FileDeletionError
)
from .utils import (
    truncate_content,
    get_file_size,
    validate_file_type,
    get_table_name_by_type,
    format_file_metadata
)


class FilesService:
    async def list_files(
        self,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        file_type: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> FileListResponse:
        """
        List files with pagination and optional filtering.
        
        Args:
            page: Page number for pagination
            page_size: Number of items per page
            file_type: Optional filter by file type
            search_query: Optional search query for title or content
            
        Returns:
            FileListResponse: Paginated list of files
            
        Raises:
            InvalidFileTypeError: If file_type is invalid
        """
        # Validate parameters
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
        
        if file_type and not validate_file_type(file_type):
            raise InvalidFileTypeError(file_type)
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        pool = await get_db_pool()
        if not pool:
            raise FileAccessError("", "Database connection not available")
        
        try:
            files: List[FileListItem] = []
            total_count = 0
            
            if file_type:
                # Query specific file type
                table_name = get_table_name_by_type(file_type)
                files, total_count = await self._query_single_table(
                    pool, table_name, file_type, page_size, offset, search_query
                )
            else:
                # Query all tables
                files, total_count = await self._query_all_tables(
                    pool, page_size, offset, search_query
                )
            
            # Calculate pagination info
            has_next = (page * page_size) < total_count
            has_previous = page > 1
            
            return FileListResponse(
                files=files,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=has_next,
                has_previous=has_previous
            )
            
        finally:
            await pool.close()

    async def get_file_detail(self, file_id: UUID, file_type: Optional[str] = None) -> FileDetailResponse:
        """
        Get detailed information about a specific file.
        
        Args:
            file_id: The ID of the file to retrieve
            file_type: Optional file type hint for faster lookup
            
        Returns:
            FileDetailResponse: Detailed file information
            
        Raises:
            FileNotFoundError: If the file is not found
            InvalidFileTypeError: If file_type is invalid
        """
        if file_type and not validate_file_type(file_type):
            raise InvalidFileTypeError(file_type)
        
        pool = await get_db_pool()
        if not pool:
            raise FileAccessError(str(file_id), "Database connection not available")
        
        try:
            if file_type:
                # Query specific table
                table_name = get_table_name_by_type(file_type)
                file_data = await self._get_file_from_table(pool, table_name, file_id)
            else:
                # Search across all tables
                file_data = await self._get_file_from_all_tables(pool, file_id)
            
            if not file_data:
                raise FileNotFoundError(str(file_id))
            
            # Get file size
            file_size = get_file_size(file_data["filepath"])
            
            # Format metadata
            metadata = format_file_metadata(
                file_data["file_type"],
                file_data["content"],
                file_data["filepath"]
            )
            
            return FileDetailResponse(
                id=file_data["id"],
                title=file_data["title"],
                filepath=file_data["filepath"],
                content=file_data["content"],
                created_at=file_data["created_at"],
                file_type=file_data["file_type"],
                file_size=file_size,
                metadata=metadata
            )
            
        finally:
            await pool.close()

    async def search_files(self, search_request: FileSearchRequest) -> FileListResponse:
        """
        Search files with advanced filtering.
        
        Args:
            search_request: Search parameters
            
        Returns:
            FileListResponse: Search results with pagination
        """
        return await self.list_files(
            page=search_request.page,
            page_size=search_request.page_size,
            file_type=search_request.file_type,
            search_query=search_request.query
        )

    async def delete_file(self, file_id: UUID, file_type: Optional[str] = None) -> FileDeleteResponse:
        """
        Delete a file from the database and filesystem.
        
        Args:
            file_id: The ID of the file to delete
            file_type: Optional file type hint for faster lookup
            
        Returns:
            FileDeleteResponse: Deletion result
            
        Raises:
            FileNotFoundError: If the file is not found
            FileDeletionError: If deletion fails
        """
        # First get the file details to find the filepath
        file_detail = await self.get_file_detail(file_id, file_type)
        
        pool = await get_db_pool()
        if not pool:
            raise FileDeletionError(str(file_id), "Database connection not available")
        
        try:
            # Delete from database
            if file_detail.file_type == FILE_TYPE_MARKDOWN:
                table_name = MARKDOWN_DOCUMENTS_TABLE
            elif file_detail.file_type == FILE_TYPE_IMAGE:
                table_name = IMAGE_DOCUMENTS_TABLE
            elif file_detail.file_type == FILE_TYPE_PDF:
                table_name = PDF_DOCUMENTS_TABLE
            else:
                raise FileDeletionError(str(file_id), f"Unknown file type: {file_detail.file_type}")
            
            async with pool.acquire() as conn:
                result = await conn.execute(
                    f"DELETE FROM {table_name} WHERE id = $1",
                    file_id
                )
                
                if result == "DELETE 0":
                    raise FileNotFoundError(str(file_id))
            
            # Delete from filesystem
            try:
                if os.path.exists(file_detail.filepath):
                    os.remove(file_detail.filepath)
            except OSError as e:
                # Log the error but don't fail the operation
                # since the database record is already deleted
                print(f"Warning: Could not delete file {file_detail.filepath}: {e}")
            
            return FileDeleteResponse(
                success=True,
                message=f"File {file_id} deleted successfully",
                deleted_file_id=file_id
            )
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileDeletionError(str(file_id), str(e))
        finally:
            await pool.close()

    async def _query_single_table(
        self,
        pool,
        table_name: str,
        file_type: str,
        page_size: int,
        offset: int,
        search_query: Optional[str]
    ) -> Tuple[List[FileListItem], int]:
        """Query a single table for files."""
        async with pool.acquire() as conn:
            # Build query with optional search
            base_query = f"SELECT id, title, filepath, content, created_at FROM {table_name}"
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            
            if search_query:
                base_query += " WHERE title ILIKE $1 OR content ILIKE $1"
                count_query += " WHERE title ILIKE $1 OR content ILIKE $1"
                search_param = f"%{search_query}%"
                
                # Get total count
                total_count = await conn.fetchval(count_query, search_param)
                
                # Get paginated results
                base_query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
                rows = await conn.fetch(base_query, search_param, page_size, offset)
            else:
                # Get total count
                total_count = await conn.fetchval(count_query)
                
                # Get paginated results
                base_query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                rows = await conn.fetch(base_query, page_size, offset)
            
            # Convert to FileListItem objects
            files = []
            for row in rows:
                files.append(FileListItem(
                    id=row["id"],
                    title=row["title"],
                    filepath=row["filepath"],
                    content_preview=truncate_content(row["content"]),
                    created_at=row["created_at"],
                    file_type=file_type
                ))
            
            return files, total_count

    async def _query_all_tables(
        self,
        pool,
        page_size: int,
        offset: int,
        search_query: Optional[str]
    ) -> Tuple[List[FileListItem], int]:
        """Query all tables and combine results."""
        all_files = []
        total_count = 0
        
        # Query each table
        for file_type, table_name in [
            (FILE_TYPE_MARKDOWN, MARKDOWN_DOCUMENTS_TABLE),
            (FILE_TYPE_IMAGE, IMAGE_DOCUMENTS_TABLE),
            (FILE_TYPE_PDF, PDF_DOCUMENTS_TABLE)
        ]:
            files, count = await self._query_single_table(
                pool, table_name, file_type, page_size * 3, 0, search_query
            )
            all_files.extend(files)
            total_count += count
        
        # Sort by created_at and apply pagination
        all_files.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        start_idx = offset
        end_idx = start_idx + page_size
        paginated_files = all_files[start_idx:end_idx]
        
        return paginated_files, total_count

    async def _get_file_from_table(self, pool, table_name: str, file_id: UUID) -> Optional[dict]:
        """Get a file from a specific table."""
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT id, title, filepath, content, created_at FROM {table_name} WHERE id = $1",
                file_id
            )
            
            if row:
                return {
                    "id": row["id"],
                    "title": row["title"],
                    "filepath": row["filepath"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                    "file_type": self._get_file_type_from_table(table_name)
                }
            return None

    async def _get_file_from_all_tables(self, pool, file_id: UUID) -> Optional[dict]:
        """Search for a file across all tables."""
        for table_name in [MARKDOWN_DOCUMENTS_TABLE, IMAGE_DOCUMENTS_TABLE, PDF_DOCUMENTS_TABLE]:
            result = await self._get_file_from_table(pool, table_name, file_id)
            if result:
                return result
        return None

    def _get_file_type_from_table(self, table_name: str) -> str:
        """Get file type from table name."""
        if table_name == MARKDOWN_DOCUMENTS_TABLE:
            return FILE_TYPE_MARKDOWN
        elif table_name == IMAGE_DOCUMENTS_TABLE:
            return FILE_TYPE_IMAGE
        elif table_name == PDF_DOCUMENTS_TABLE:
            return FILE_TYPE_PDF
        else:
            raise ValueError(f"Unknown table: {table_name}")


# Export a singleton instance
files_service = FilesService()
