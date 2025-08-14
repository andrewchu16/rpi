from datetime import timedelta

from models.auth import LoginSuccess
from security.token import create_access_token
from security.config import ACCESS_CODE, ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    @staticmethod
    def login(password: str) -> LoginSuccess:
        # Validate access code
        if password != ACCESS_CODE:
            raise ValueError("Invalid access code")

        # Create access token with expiration
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(expires_delta=access_token_expires)

        return LoginSuccess(access_token=access_token, token_type="bearer")