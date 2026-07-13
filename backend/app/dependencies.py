"""FastAPI-facing auth dependencies. Business logic lives in services.AuthService;
this module's only job is translating between HTTP/Depends and that service.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.exceptions import UnauthorizedError
from app.database import get_session
from app.models import User, UserRole
from app.repositories import UserRepository
from app.services import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(session))


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return auth_service.get_current_user(token)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_role(*roles: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    return checker
