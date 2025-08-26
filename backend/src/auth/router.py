from fastapi import APIRouter
from .schemas import LoginSuccess, LoginRequest
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginSuccess)
async def login(login_request: LoginRequest) -> LoginSuccess:
    """
    Authenticate using the access code to get a JWT token.
    
    The username field is ignored, only the password is checked against the access code.
    """
    return AuthService.login(login_request.password)
