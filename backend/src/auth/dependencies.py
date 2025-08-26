from fastapi import Depends
from .utils import verify_access_token
from .schemas import Token


def get_current_user(token: Token = Depends(verify_access_token)) -> Token:
    """
    Dependency to get the current authenticated user from the JWT token.
    
    Args:
        token: The verified JWT token
        
    Returns:
        Token: The token containing user authentication information
    """
    return token
