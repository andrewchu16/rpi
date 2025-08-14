from .auth_routes import router as auth_router
from .health_routes import router as health_router
from .upload_routes import router as upload_router

__all__ = [
    "auth_router",
    "health_router",
    "upload_router"
]