from sqlalchemy import func
from sqlmodel import Session, select

from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        stmt = select(User).where(func.lower(User.email) == normalized)
        return self.session.exec(stmt).first()
