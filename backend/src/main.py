from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .config import config
from .database import init_db, close_db
from .chat import chat_router
from .chat.controller import chat_controller

# Import models to ensure they are registered with Base.metadata
from .chat.models import Message, CacheInfo, ProcessingInfo

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("Starting the application")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Preload ML models during startup
    logger.info("Preloading ML models...")
    chat_controller.llm.preload_model()
    chat_controller.embedding.preload_model()
    logger.info("ML models preloaded successfully")
    
    yield
    
    logger.info("Shutting down the application")
    # Cleanup database
    await close_db()
    logger.info("Database connection closed")


app = FastAPI(lifespan=lifespan, openapi_url="/openapi.json" if config.debug else None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "welcome to the andrew chu api", "server_time": datetime.now()}


app.include_router(chat_router)
