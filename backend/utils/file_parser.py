from PIL import Image
import pytesseract
from io import BytesIO

def get_md_content(markdown_bytes: bytes) -> str:
    """
    Convert markdown document from bytes to string.
    
    Args:
        markdown_bytes: The markdown document as bytes
        
    Returns:
        The markdown document as a string
    """
    return markdown_bytes.decode('utf-8')

def get_image_content(image_bytes: bytes) -> str:
    """
    Extracts text content from an image using OCR.

    Args:
        image_bytes (bytes): The image file in bytes.

    Returns:
        str: The extracted text content from the image.
    """
    # Open the image from bytes
    image = Image.open(BytesIO(image_bytes))

    # Convert the image to grayscale
    gray_image = image.convert('L')

    # Apply thresholding to binarize the image
    binary_image = gray_image.point(lambda x: 0 if x < 128 else 255, '1')

    # Use pytesseract to extract text
    text = pytesseract.image_to_string(binary_image)

    return text
