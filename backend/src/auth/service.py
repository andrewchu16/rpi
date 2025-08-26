from datetime import timedelta
import logging
from typing import Optional

from .schemas import LoginSuccess
from .utils import create_access_token
from .config import auth_settings
from .exceptions import InvalidAccessCodeError


class AuthService:
    def __init__(self) -> None:
        self.logger = logging.getLogger("auth.login")
    
    def login(self, password: str, ip_address: Optional[str] = None) -> LoginSuccess:
        """
        Authenticate user with access code and return JWT token.
        
        Args:
            password: The access code for authentication
            ip_address: Optional IP address (for logging purposes)
            
        Returns:
            LoginSuccess: Object containing the access token and token type
            
        Raises:
            InvalidAccessCodeError: If the access code is incorrect
        """
        # Validate access code
        if password != auth_settings.access_code:
            self.logger.warning(f"Failed login attempt - IP: {ip_address or 'unknown'}")
            raise InvalidAccessCodeError()

        # Log successful login
        self.logger.info(f"Successful login - IP: {ip_address or 'unknown'}")

        # Create access token with expiration
        access_token_expires = timedelta(minutes=auth_settings.access_token_expire_minutes)
        access_token = create_access_token(expires_delta=access_token_expires)

        return LoginSuccess(access_token=access_token, token_type="bearer")


# Export a singleton instance
auth_service = AuthService()
