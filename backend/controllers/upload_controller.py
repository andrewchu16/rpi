from fastapi import UploadFile, HTTPException, status
from config import MAX_FILE_SIZE
from services import UploadService


class UploadController:
    @staticmethod
    def _check_file_size(file: UploadFile) -> int:
        """Check if the file size is within the allowed limit."""
        file.file.seek(0, 2)  # Seek to the end of the file
        file_size = file.file.tell()  # Get current position (file size)
        file.file.seek(0)  # Reset file pointer to the beginning

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE/1024/1024:.1f}MB",
            )

        return file_size

    @staticmethod
    async def upload_markdown(file: UploadFile):
        """Guard and delegate markdown processing to service."""
        # Check file size
        file_size = UploadController._check_file_size(file)

        # Verify it's a text file
        content_type = file.content_type or ""
        if not (content_type.startswith("text/") or "markdown" in content_type.lower()):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File must be a text/markdown file",
            )

        # Read content to verify it's plaintext
        content = await file.read()
        try:
            _ = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File must contain valid UTF-8 text",
            ) from exc

        # Reset pointer for service to re-read if needed
        file.file.seek(0)

        # Delegate to service
        return await UploadService.process_markdown(file, file_size)

    @staticmethod
    async def upload_image(file: UploadFile):
        """Guard and delegate image processing to service."""
        # Check file size
        file_size = UploadController._check_file_size(file)

        # Verify it's an image file
        content_type = file.content_type or ""
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File must be an image",
            )

        # Delegate to service for actual processing
        return await UploadService.process_image(file, file_size)
