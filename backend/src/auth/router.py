from fastapi import APIRouter, Request
from .schemas import LoginSuccess, LoginRequest
from .service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginSuccess)
async def login(login_request: LoginRequest, request: Request) -> LoginSuccess:
    """
    Authenticate using the access code to get a JWT token.
    
    Only the password is checked against the access code.
    """
    # Extract client IP address
    client_ip = request.client.host if request.client else "unknown"
    
    return auth_service.login(
        password=login_request.password,
        ip_address=client_ip
    )
