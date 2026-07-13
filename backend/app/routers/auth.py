from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import models, schemas
from app.core.exceptions import UnauthorizedError
from app.dependencies import get_auth_service, get_current_user
from app.services import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.authenticate(form_data.username, form_data.password)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    token = auth_service.issue_token(user)
    return schemas.Token(access_token=token)


@router.get("/auth/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
