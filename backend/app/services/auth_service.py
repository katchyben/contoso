import jwt

from app import models
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, verify_password
from app.repositories import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, email: str, password: str) -> models.User:
        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        return user

    def issue_token(self, user: models.User) -> str:
        return create_access_token(subject=user.email, role=user.role.value)

    def get_current_user(self, token: str) -> models.User:
        try:
            payload = decode_access_token(token)
            email = payload.get("sub")
            if email is None:
                raise UnauthorizedError()
        except jwt.PyJWTError as exc:
            raise UnauthorizedError() from exc

        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            raise UnauthorizedError()
        return user
