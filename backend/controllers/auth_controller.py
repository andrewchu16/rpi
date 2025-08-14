from fastapi import HTTPException, status
import services.auth_service as auth_service


def login(password: str):
    try:
        return auth_service.login(password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect access code",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e