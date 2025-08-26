from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.router import router as auth_router
from .health.router import router as health_router
from .upload.router import router as upload_router

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

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(upload_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

