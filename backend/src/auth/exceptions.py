from fastapi import HTTPException, status
from .constants import (
    INVALID_ACCESS_CODE_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    TOKEN_NOT_VALID_MESSAGE,
    INVALID_TOKEN_MESSAGE,
    INVALID_CREDENTIALS_MESSAGE,
    WWW_AUTHENTICATE_HEADER
)


class AuthenticationError(HTTPException):
    """Base authentication error"""
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": WWW_AUTHENTICATE_HEADER}
        )


class InvalidAccessCodeError(AuthenticationError):
    """Raised when the access code is incorrect"""
    def __init__(self):
        super().__init__(detail=INVALID_ACCESS_CODE_MESSAGE)


class TokenExpiredError(AuthenticationError):
    """Raised when the JWT token has expired"""
    def __init__(self):
        super().__init__(detail=TOKEN_EXPIRED_MESSAGE)


class TokenNotValidError(AuthenticationError):
    """Raised when the JWT token is not yet valid"""
    def __init__(self):
        super().__init__(detail=TOKEN_NOT_VALID_MESSAGE)


class InvalidTokenError(AuthenticationError):
    """Raised when the JWT token is invalid"""
    def __init__(self):
        super().__init__(detail=INVALID_TOKEN_MESSAGE)


class InvalidCredentialsError(AuthenticationError):
    """Raised when authentication credentials are invalid"""
    def __init__(self):
        super().__init__(detail=INVALID_CREDENTIALS_MESSAGE)
