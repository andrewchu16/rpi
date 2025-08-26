from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import auth_settings
from .schemas import Token
from .exceptions import (
    TokenExpiredError,
    TokenNotValidError,
    InvalidTokenError,
    InvalidCredentialsError
)

# Bearer token setup
bearer_scheme = HTTPBearer()


def create_access_token(*, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=auth_settings.access_token_expire_minutes)

    to_encode: Token = Token(iat=datetime.now(timezone.utc), exp=expire)

    encoded_jwt = jwt.encode(to_encode.model_dump(), auth_settings.secret_key, algorithm=auth_settings.algorithm)
    return encoded_jwt


def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Token:
    """Verify the JWT token from the Authorization header"""
    try:
        payload = jwt.decode(credentials.credentials, auth_settings.secret_key, algorithms=[auth_settings.algorithm])
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidIssuedAtError:
        raise TokenNotValidError()
    except jwt.DecodeError:
        raise InvalidTokenError()
    except jwt.PyJWTError:
        raise InvalidCredentialsError()

    return Token(**payload)
