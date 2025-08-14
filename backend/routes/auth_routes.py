from fastapi import APIRouter
from controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(password: str):
    """
    Authenticate using the access code to get a JWT token.
    
    The username field is ignored, only the password is checked against the access code.
    """
    return auth_controller.login(password)
