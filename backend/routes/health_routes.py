from fastapi import APIRouter, Depends
from datetime import datetime

from security.token import verify_access_token
from models.auth import Token


router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@router.get("/login")
async def health_login(token: Token = Depends(verify_access_token)):
    """
    Health check endpoint that requires a valid JWT token.
    
    This endpoint is protected and will return the token information if the token is valid.
    """
    return {"status": "healthy", "token_info": token.model_dump()}