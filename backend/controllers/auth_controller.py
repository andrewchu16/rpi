from fastapi import HTTPException, status
from models.auth import LoginSuccess
from services import AuthService


class AuthController:
    @staticmethod
    def login(password: str) -> LoginSuccess:
        try:
            return AuthService.login(password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect access code",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e