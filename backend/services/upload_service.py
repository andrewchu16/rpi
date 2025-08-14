from fastapi import UploadFile
from PIL import Image
import io

class UploadService:
    @staticmethod
    async def process_markdown(file: UploadFile, size: int):
        """
        Process a valid markdown/text file.
        Assumes guards (size/content-type/encoding) have already run.
        """
        content = await file.read()
        text_content = content.decode("utf-8")
        # Example return; real logic (e.g., save, parse) would go here
        return {
            "filename": file.filename,
            "size": size,
            "content_type": file.content_type,
            "text_length": len(text_content),
        }

    @staticmethod
    async def process_image(file: UploadFile, size: int):
        """
        Process a valid image file and return metadata and the Pillow image.
        """
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        width, height = image.size
        img_format = image.format
        mode = image.mode
        return {
            "filename": file.filename,
            "size": size,
            "content_type": file.content_type,
            "width": width,
            "height": height,
            "format": img_format,
            "mode": mode,
            "image": image,
        }
