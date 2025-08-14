import os
from dotenv import load_dotenv


load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# This is the password that will protect your API
# In production, set this via environment variable
ACCESS_CODE = os.getenv("ACCESS_CODE", "your-secure-access-code")
