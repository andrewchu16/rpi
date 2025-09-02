from contextlib import asynccontextmanager
import json
import logging
import logging.config
import atexit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from logging.handlers import QueueHandler
from .chat import chat_router
from .config import config
from .database import init_db, close_db

# Setup logging at module level
def setup_logging():
    with open("./logging_config.json", "r") as f:
        logging.config.dictConfig(json.load(f))
    queue_handler: QueueHandler = logging.getHandlerByName("queue_handler")

    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("Starting the application")
    # Initialize database
    await init_db()
    logger.info("Database initialized")
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
