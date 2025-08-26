from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Timestamp of the health check")


class HealthLoginResponse(BaseModel):
    """Response model for authenticated health check endpoint."""
    status: str = Field(..., description="Health status")
    token_info: Dict[str, Any] = Field(..., description="JWT token information")
