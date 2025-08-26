import json
import logging
import logging.config
import atexit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.router import router as auth_router
from .health.router import router as health_router
from .upload.router import router as upload_router
from logging.handlers import QueueHandler

app = FastAPI()

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

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
logger.info("Starting the application")

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(upload_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

