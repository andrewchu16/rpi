import os
from dotenv import load_dotenv


load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(4 * 1024 * 1024)))

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/")

# Database Configuration
DATABASE_HOST = os.getenv("DATABASE_HOST", "db")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rpi_db")