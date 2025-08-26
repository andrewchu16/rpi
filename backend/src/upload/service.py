import os
from fastapi import UploadFile
from typing import Optional, List, Union
from ..database import get_db_pool
from .models import MarkdownDocument, ImageDocument, PDFDocument
from .schemas import (
    MarkdownUploadResponse, 
    ImageUploadResponse, 
    PDFUploadResponse,
    BulkUploadResponse,
    BulkUploadItem
)
from .utils import (
    save_file_to_disk,
    get_image_metadata,
    get_pdf_metadata,
    MARKDOWN_UPLOAD_SUBDIR,
    IMAGE_UPLOAD_SUBDIR,
    PDF_UPLOAD_SUBDIR
)


class UploadService:
    async def process_markdown(self, file: UploadFile, size: int) -> MarkdownUploadResponse:
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

    async def process_image(self, file: UploadFile, size: int) -> ImageUploadResponse:
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

    async def process_pdf(self, file: UploadFile, size: int) -> PDFUploadResponse:
        """
        Process a valid PDF file and return metadata.
        
        Args:
            file: The uploaded PDF file
            size: Size of the file in bytes
            
        Returns:
            PDFUploadResponse: Response with file upload information
        """
        content = await file.read()
        page_count, extracted_text = get_pdf_metadata(content)
        
        # Create PDF document instance
        pdf_doc = PDFDocument(
            title=file.filename,
            content=extracted_text,
            filepath=""  # Will be set after saving file
        )
        
        # Save file with document ID as filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
        filename = f"{pdf_doc.id}{file_extension}"
        filepath = save_file_to_disk(content, filename, PDF_UPLOAD_SUBDIR)
        
        # Update document with filepath
        pdf_doc.filepath = filepath
        
        # Save to database
        pool = await get_db_pool()
        if pool:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO pdf_documents (id, title, filepath, content, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, pdf_doc.id, pdf_doc.title, pdf_doc.filepath, 
                     pdf_doc.content, pdf_doc.created_at)
            await pool.close()
        
        return PDFUploadResponse(
            filename=file.filename,
            size=size,
            content_type=file.content_type,
            page_count=page_count,
            text_length=len(extracted_text),
            document_id=pdf_doc.id,
            filepath=pdf_doc.filepath
        )

    async def process_bulk_upload(self, files: List[UploadFile]) -> BulkUploadResponse:
        """
        Process multiple files of different types in a single request.
        
        Args:
            files: List of uploaded files
            
        Returns:
            BulkUploadResponse: Response with results for all files
        """
        results: List[BulkUploadItem] = []
        successful_uploads = 0
        failed_uploads = 0
        
        for file in files:
            try:
                # Determine file type and process accordingly
                content_type = file.content_type or ""
                
                if any(allowed_type in content_type.lower() for allowed_type in ["text/markdown", "text/plain", "text/x-markdown", "application/markdown"]):
                    # Process as markdown
                    file_size = await self._get_file_size(file)
                    result = await self.process_markdown(file, file_size)
                    results.append(BulkUploadItem(
                        filename=file.filename,
                        success=True,
                        message="Markdown file processed successfully",
                        file_info=result
                    ))
                    successful_uploads += 1
                    
                elif content_type.startswith("image/"):
                    # Process as image
                    file_size = await self._get_file_size(file)
                    result = await self.process_image(file, file_size)
                    results.append(BulkUploadItem(
                        filename=file.filename,
                        success=True,
                        message="Image processed successfully",
                        file_info=result
                    ))
                    successful_uploads += 1
                    
                elif content_type == "application/pdf":
                    # Process as PDF
                    file_size = await self._get_file_size(file)
                    result = await self.process_pdf(file, file_size)
                    results.append(BulkUploadItem(
                        filename=file.filename,
                        success=True,
                        message="PDF processed successfully",
                        file_info=result
                    ))
                    successful_uploads += 1
                    
                else:
                    # Unsupported file type
                    results.append(BulkUploadItem(
                        filename=file.filename,
                        success=False,
                        message=f"Unsupported file type: {content_type}",
                        file_info=None
                    ))
                    failed_uploads += 1
                    
            except Exception as e:
                # Handle any processing errors
                results.append(BulkUploadItem(
                    filename=file.filename,
                    success=False,
                    message=f"Processing failed: {str(e)}",
                    file_info=None
                ))
                failed_uploads += 1
        
        return BulkUploadResponse(
            total_files=len(files),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            results=results
        )

    async def _get_file_size(self, file: UploadFile) -> int:
        """
        Get file size for processing.
        
        Args:
            file: The uploaded file
            
        Returns:
            int: File size in bytes
        """
        file.file.seek(0, 2)  # Seek to the end
        size = file.file.tell()  # Get current position (file size)
        file.file.seek(0)  # Reset to beginning
        return size


# Export a singleton instance
upload_service = UploadService()
