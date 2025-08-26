# Files Module

The Files module provides functionality for viewing and managing uploaded documents in the RPI backend application.

## Overview

This module allows users to:
- List uploaded files with pagination
- View detailed information about specific files
- Search files by title or content
- Delete files from both database and filesystem
- Filter files by type (markdown, image, PDF)

## Architecture

The module follows the established backend architecture pattern:

- **Router** (`router.py`): FastAPI endpoints for HTTP requests
- **Service** (`service.py`): Business logic for file operations
- **Schemas** (`schemas.py`): Pydantic models for request/response validation
- **Constants** (`constants.py`): Module constants and configuration
- **Exceptions** (`exceptions.py`): Custom exception classes
- **Utils** (`utils.py`): Utility functions

## API Endpoints

### List Files
```
GET /files/
```

**Query Parameters:**
- `page` (int, default: 1): Page number for pagination
- `page_size` (int, default: 20, max: 100): Number of items per page
- `file_type` (str, optional): Filter by file type (markdown, image, pdf)
- `search` (str, optional): Search query for title or content

**Response:**
```json
{
  "files": [
    {
      "id": "uuid",
      "title": "Document Title",
      "filepath": "/path/to/file",
      "content_preview": "First 200 characters...",
      "created_at": "2024-01-01T00:00:00Z",
      "file_type": "markdown"
    }
  ],
  "total_count": 100,
  "page": 1,
  "page_size": 20,
  "has_next": true,
  "has_previous": false
}
```

### Get File Detail
```
GET /files/{file_id}
```

**Path Parameters:**
- `file_id` (UUID): The ID of the file to retrieve

**Query Parameters:**
- `file_type` (str, optional): File type hint for faster lookup

**Response:**
```json
{
  "id": "uuid",
  "title": "Document Title",
  "filepath": "/path/to/file",
  "content": "Full document content",
  "created_at": "2024-01-01T00:00:00Z",
  "file_type": "markdown",
  "file_size": 1024,
  "metadata": {
    "file_type": "markdown",
    "content_length": 500,
    "filepath": "/path/to/file",
    "content_type": "text/markdown"
  }
}
```

### Search Files
```
POST /files/search
```

**Request Body:**
```json
{
  "query": "search term",
  "file_type": "markdown",
  "page": 1,
  "page_size": 20
}
```

**Response:** Same as List Files endpoint

### Delete File
```
DELETE /files/{file_id}
```

**Path Parameters:**
- `file_id` (UUID): The ID of the file to delete

**Query Parameters:**
- `file_type` (str, optional): File type hint for faster lookup

**Response:**
```json
{
  "success": true,
  "message": "File uuid deleted successfully",
  "deleted_file_id": "uuid"
}
```

### Get Supported File Types
```
GET /files/types/supported
```

**Response:**
```json
{
  "supported_types": ["markdown", "image", "pdf"],
  "description": "List of supported file types for viewing and management"
}
```

## Database Tables

The module works with the following database tables:
- `markdown_documents`: Markdown and text files
- `image_documents`: Image files
- `pdf_documents`: PDF files

Each table contains:
- `id` (UUID): Primary key
- `title` (VARCHAR): File title
- `filepath` (TEXT): Path to the file on disk
- `content` (TEXT): File content (text for documents, filename for images)
- `created_at` (TIMESTAMP): Creation timestamp

## Error Handling

The module provides custom exceptions:
- `FileNotFoundError`: When a file is not found
- `InvalidFileTypeError`: When an invalid file type is specified
- `FileAccessError`: When there's an error accessing a file
- `FileDeletionError`: When there's an error deleting a file

All exceptions are properly converted to HTTP responses with appropriate status codes.

## Usage Examples

### List all files
```python
from src.files.service import files_service

# List first page of all files
result = await files_service.list_files(page=1, page_size=20)
```

### Search for markdown files
```python
# Search for markdown files containing "python"
result = await files_service.list_files(
    file_type="markdown",
    search_query="python"
)
```

### Get file details
```python
from uuid import UUID

# Get details of a specific file
file_id = UUID("12345678-1234-1234-1234-123456789012")
file_detail = await files_service.get_file_detail(file_id)
```

### Delete a file
```python
# Delete a file
delete_result = await files_service.delete_file(file_id)
```

## Testing

Run the test script to verify the module functionality:

```bash
cd backend
python test_files_module.py
```

## Integration

The files module is automatically integrated into the main FastAPI application in `src/main.py`. The router is included with the prefix `/files` and tagged as "files" for API documentation.
