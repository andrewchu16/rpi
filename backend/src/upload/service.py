import os
from fastapi import UploadFile
from typing import Optional
from ..database import get_db_pool
from .models import MarkdownDocument, ImageDocument
from .schemas import MarkdownUploadResponse, ImageUploadResponse
from .utils import (
    save_file_to_disk,
    get_image_metadata,
    MARKDOWN_UPLOAD_SUBDIR,
    IMAGE_UPLOAD_SUBDIR
)


class UploadService:
    @staticmethod
    async def process_markdown(file: UploadFile, size: int) -> MarkdownUploadResponse:
        """
        Process a valid markdown/text file.
        Assumes guards (size/content-type/encoding) have already run.
        
        Args:
            file: The uploaded markdown file
            size: Size of the file in bytes
            
        Returns:
            MarkdownUploadResponse: Response with file upload information
        """
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # Create markdown document instance
        markdown_doc = MarkdownDocument(
            title=file.filename,
            content=text_content,
            filepath=""  # Will be set after saving file
        )
        
        # Save file with document ID as filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".md"
        filename = f"{markdown_doc.id}{file_extension}"
        filepath = save_file_to_disk(content, filename, MARKDOWN_UPLOAD_SUBDIR)
        
        # Update document with filepath
        markdown_doc.filepath = filepath
        
        # Save to database
        pool = await get_db_pool()
        if pool:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO markdown_documents (id, title, filepath, content, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, markdown_doc.id, markdown_doc.title, markdown_doc.filepath, 
                     markdown_doc.content, markdown_doc.created_at)
            await pool.close()
        
        return MarkdownUploadResponse(
            filename=file.filename,
            size=size,
            content_type=file.content_type,
            text_length=len(text_content),
            document_id=markdown_doc.id,
            filepath=markdown_doc.filepath
        )

    @staticmethod
    async def process_image(file: UploadFile, size: int) -> ImageUploadResponse:
        """
        Process a valid image file and return metadata.
        
        Args:
            file: The uploaded image file
            size: Size of the file in bytes
            
        Returns:
            ImageUploadResponse: Response with file upload information
        """
        content = await file.read()
        width, height, img_format, mode = get_image_metadata(content)
        
        # Create image document instance
        image_doc = ImageDocument(
            title=file.filename,
            content=file.filename,  # Set content to filename as requested
            filepath=""  # Will be set after saving file
        )
        
        # Save file with document ID as filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{image_doc.id}{file_extension}"
        filepath = save_file_to_disk(content, filename, IMAGE_UPLOAD_SUBDIR)
        
        # Update document with filepath
        image_doc.filepath = filepath
        
        # Save to database
        pool = await get_db_pool()
        if pool:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO image_documents (id, title, filepath, content, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, image_doc.id, image_doc.title, image_doc.filepath, 
                     image_doc.content, image_doc.created_at)
            await pool.close()
        
        return ImageUploadResponse(
            filename=file.filename,
            size=size,
            content_type=file.content_type,
            width=width,
            height=height,
            format=img_format,
            mode=mode,
            document_id=image_doc.id,
            filepath=image_doc.filepath
        )
