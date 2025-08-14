import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
