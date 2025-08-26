from fastapi import APIRouter, Depends
from datetime import datetime
from ..auth.dependencies import get_current_user
from ..auth.schemas import Token
from .schemas import HealthResponse, HealthLoginResponse
from .constants import HEALTH_STATUS

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    """
    return HealthResponse(status=HEALTH_STATUS, timestamp=datetime.now())


@router.get("/login", response_model=HealthLoginResponse)
async def health_login(token: Token = Depends(get_current_user)) -> HealthLoginResponse:
    """
    Health check endpoint that requires a valid JWT token.
    
    This endpoint is protected and will return the token information if the token is valid.
    """
    return HealthLoginResponse(
        status=HEALTH_STATUS,
        token_info=token.model_dump()
    )
