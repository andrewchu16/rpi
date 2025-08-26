from datetime import timedelta

from .schemas import LoginSuccess
from .utils import create_access_token
from .config import auth_settings
from .exceptions import InvalidAccessCodeError


class AuthService:
    @staticmethod
    def login(password: str) -> LoginSuccess:
        """
        Authenticate user with access code and return JWT token.
        
        Args:
            password: The access code for authentication
            
        Returns:
            LoginSuccess: Object containing the access token and token type
            
        Raises:
            InvalidAccessCodeError: If the access code is incorrect
        """
        # Validate access code
        if password != auth_settings.access_code:
            raise InvalidAccessCodeError()

        # Create access token with expiration
        access_token_expires = timedelta(minutes=auth_settings.access_token_expire_minutes)
        access_token = create_access_token(expires_delta=access_token_expires)

        return LoginSuccess(access_token=access_token, token_type="bearer")
